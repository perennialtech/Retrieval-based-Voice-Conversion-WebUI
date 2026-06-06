import logging
import os
import traceback

logger = logging.getLogger(__name__)

from pathlib import Path
from time import time

import faiss
import librosa
import numpy as np
import torch
import torch.nn.functional as F
from scipy import signal

from rvc_webui.rvc.f0 import Generator

bh, ah = signal.butter(N=5, Wn=48, btype="high", fs=16000)


def change_rms(data1, sr1, data2, sr2, rate):  # 1是输入音频，2是输出音频,rate是2的占比
    # print(data1.max(),data2.max())
    rms1 = librosa.feature.rms(
        y=data1, frame_length=sr1 // 2 * 2, hop_length=sr1 // 2
    )  # 每半秒一个点
    rms2 = librosa.feature.rms(y=data2, frame_length=sr2 // 2 * 2, hop_length=sr2 // 2)
    rms1 = torch.from_numpy(rms1).float()
    rms1 = F.interpolate(
        rms1.unsqueeze(0), size=data2.shape[0], mode="linear"
    ).squeeze()
    rms2 = torch.from_numpy(rms2).float()
    rms2 = F.interpolate(
        rms2.unsqueeze(0), size=data2.shape[0], mode="linear"
    ).squeeze()
    rms2 = rms2.clamp_min_(1e-6)
    data2 *= rms1.pow(1 - rate).mul_(rms2.pow(rate - 1)).numpy()
    return data2


class Pipeline:
    def __init__(self, tgt_sr, config):
        self.x_pad, self.x_query, self.x_center, self.x_max, self.is_half = (
            config.x_pad,
            config.x_query,
            config.x_center,
            config.x_max,
            config.is_half,
        )
        self.sr = 16000  # hubert输入采样率
        self.window = 160  # 每帧点数
        self.t_pad = self.sr * self.x_pad  # 每条前后pad时间
        self.t_pad_tgt = tgt_sr * self.x_pad
        self.t_pad2 = self.t_pad * 2
        self.t_query = self.sr * self.x_query  # 查询切点前后查询时间
        self.t_center = self.sr * self.x_center  # 查询切点位置
        self.t_max = self.sr * self.x_max  # 免查询时长阈值
        self.device = config.device
        self._torch_device = torch.device(self.device)

        self._faiss_gpu_resources = None
        if self._torch_device.type == "cuda":
            try:
                import faiss.contrib.torch_utils  # noqa: F401

                self._faiss_gpu_resources = faiss.StandardGpuResources()
            except Exception:
                logger.debug(
                    "FAISS GPU is unavailable; using CPU FAISS.",
                    exc_info=True,
                )

        self.f0_gen = Generator(
            Path(os.environ["rmvpe_root"]),
            self.is_half,
            self.x_pad,
            self.device,
            self.window,
            self.sr,
        )
        self._index_cache_key = None
        self._index_cache_value = (None, None)

    def _load_index(self, file_index, index_rate):
        if not file_index or index_rate == 0:
            return None, None

        try:
            stat = os.stat(file_index)
        except OSError:
            return None, None

        cache_key = (
            file_index,
            stat.st_mtime_ns,
            stat.st_size,
            str(self.device),
            self.is_half,
        )
        if cache_key == self._index_cache_key:
            return self._index_cache_value

        try:
            cpu_index = faiss.read_index(file_index)
            big_npy = cpu_index.reconstruct_n(0, cpu_index.ntotal)
        except Exception:
            traceback.print_exc()
            return None, None

        index = cpu_index
        if self._faiss_gpu_resources is not None:
            try:
                device_id = (
                    self._torch_device.index
                    if self._torch_device.index is not None
                    else torch.cuda.current_device()
                )
                gpu_index = faiss.index_cpu_to_gpu(
                    self._faiss_gpu_resources,
                    device_id,
                    cpu_index,
                )
                dtype = torch.float16 if self.is_half else torch.float32
                big_npy = torch.as_tensor(big_npy, device=self.device, dtype=dtype)
                index = gpu_index
            except Exception:
                logger.debug(
                    "Failed to move FAISS index to CUDA; using CPU FAISS.",
                    exc_info=True,
                )

        self._index_cache_key = cache_key
        self._index_cache_value = (index, big_npy)
        return index, big_npy

    def vc(
        self,
        model,
        net_g,
        sid,
        audio0,
        pitch,
        pitchf,
        times,
        index,
        big_npy,
        index_rate,
        version,
        protect,
    ):  # ,file_index,file_big_npy
        feats = torch.from_numpy(audio0)
        if feats.dim() == 2:  # double channels
            feats = feats.mean(-1)
        assert feats.dim() == 1, feats.dim()

        dtype = torch.float16 if self.is_half else torch.float32
        feats = feats.view(1, -1).to(device=self.device, dtype=dtype)
        padding_mask = torch.zeros(feats.shape, dtype=torch.bool, device=self.device)

        inputs = {
            "source": feats,
            "padding_mask": padding_mask,
            "output_layer": 9 if version == "v1" else 12,
        }
        t0 = time()
        with torch.inference_mode():
            logits = model.extract_features(**inputs)
            feats = model.final_proj(logits[0]) if version == "v1" else logits[0]
        if protect < 0.5 and pitch is not None and pitchf is not None:
            feats0 = feats.clone()
        if index is not None and big_npy is not None and index_rate != 0:
            if isinstance(big_npy, torch.Tensor):
                npy = feats[0].contiguous().float()
                try:
                    score, ix = index.search(npy, k=8)
                except Exception as exc:
                    raise Exception("index mismatch") from exc

                if not isinstance(score, torch.Tensor):
                    score = torch.as_tensor(score, device=self.device)
                else:
                    score = score.to(device=self.device)

                if not isinstance(ix, torch.Tensor):
                    ix = torch.as_tensor(ix, device=self.device)
                else:
                    ix = ix.to(device=self.device)

                ix = ix.long()
                score = score.clamp_min(1e-8)
                weight = score.reciprocal().square()
                weight = weight / weight.sum(dim=1, keepdim=True)
                npy = (big_npy[ix] * weight.unsqueeze(-1)).sum(dim=1)
                feats = (
                    npy.unsqueeze(0).to(dtype=feats.dtype).mul(index_rate)
                    + (1 - index_rate) * feats
                )
            else:
                npy = feats[0].cpu().numpy()
                if self.is_half:
                    npy = npy.astype("float32")

                # _, I = index.search(npy, 1)
                # npy = big_npy[Isqueeze()]

                try:
                    score, ix = index.search(npy, k=8)
                except Exception as exc:
                    raise Exception("index mismatch") from exc
                np.maximum(score, 1e-8, out=score)
                weight = np.reciprocal(score)
                np.square(weight, out=weight)
                weight /= weight.sum(axis=1, keepdims=True)
                npy = np.sum(big_npy[ix] * np.expand_dims(weight, axis=2), axis=1)

                if self.is_half:
                    npy = npy.astype("float16")
                feats = (
                    torch.from_numpy(npy).unsqueeze(0).to(self.device) * index_rate
                    + (1 - index_rate) * feats
                )

        feats = F.interpolate(feats.permute(0, 2, 1), scale_factor=2).permute(0, 2, 1)
        if protect < 0.5 and pitch is not None and pitchf is not None:
            feats0 = F.interpolate(feats0.permute(0, 2, 1), scale_factor=2).permute(
                0, 2, 1
            )
        t1 = time()
        p_len = audio0.shape[0] // self.window
        if feats.shape[1] < p_len:
            p_len = feats.shape[1]
            if pitch is not None and pitchf is not None:
                pitch = pitch[:, :p_len]
                pitchf = pitchf[:, :p_len]

        if protect < 0.5 and pitch is not None and pitchf is not None:
            pitchff = pitchf.clone()
            pitchff[pitchf > 0] = 1
            pitchff[pitchf < 1] = protect
            pitchff = pitchff.unsqueeze(-1)
            feats = feats * pitchff + feats0 * (1 - pitchff)
            feats = feats.to(feats0.dtype)
        p_len = torch.tensor([p_len], device=self.device).long()
        with torch.inference_mode():
            audio1 = (
                net_g.infer(
                    feats,
                    p_len,
                    sid,
                    pitch=pitch,
                    pitchf=pitchf,
                )[0, 0]
                .detach()
                .cpu()
                .float()
                .numpy()
            )
        del feats, p_len, padding_mask
        t2 = time()
        times[0] += t1 - t0
        times[2] += t2 - t1
        return audio1

    def pipeline(
        self,
        model,
        net_g,
        sid,
        audio,
        times,
        f0_up_key,
        f0_method,
        file_index,
        index_rate,
        if_f0,
        filter_radius,
        tgt_sr,
        resample_sr,
        rms_mix_rate,
        version,
        protect,
        f0_file=None,
    ):
        index, big_npy = self._load_index(file_index, index_rate)
        audio = signal.filtfilt(bh, ah, audio)
        audio_pad = np.pad(audio, (self.window // 2, self.window // 2), mode="reflect")
        opt_ts = []
        if audio_pad.shape[0] > self.t_max:
            audio_sum = np.zeros_like(audio)
            for i in range(self.window):
                audio_sum += np.abs(audio_pad[i : i - self.window])
            for t in range(self.t_center, audio.shape[0], self.t_center):
                opt_ts.append(
                    t
                    - self.t_query
                    + np.where(
                        audio_sum[t - self.t_query : t + self.t_query]
                        == audio_sum[t - self.t_query : t + self.t_query].min()
                    )[0][0]
                )
        s = 0
        audio_opt = []
        t = None
        t1 = time()
        audio_pad = np.pad(audio, (self.t_pad, self.t_pad), mode="reflect")
        p_len = audio_pad.shape[0] // self.window
        inp_f0 = None
        if hasattr(f0_file, "name"):
            try:
                with open(f0_file.name) as f:
                    raw_lines = f.read()
                    if len(raw_lines) > 0:
                        lines = raw_lines.strip("\n").split("\n")
                        inp_f0 = []
                        for line in lines:
                            inp_f0.append([float(i) for i in line.split(",")])
                        inp_f0 = np.array(inp_f0, dtype="float32")
            except:
                traceback.print_exc()
        sid = torch.tensor(sid, device=self.device).unsqueeze(0).long()
        pitch, pitchf = None, None
        if if_f0:
            if if_f0 == 1:
                pitch, pitchf = self.f0_gen.calculate(
                    audio_pad,
                    p_len,
                    f0_up_key,
                    f0_method,
                    filter_radius,
                    inp_f0,
                )
            elif if_f0 == 2:
                pitch, pitchf = f0_method
            pitch = pitch[:p_len]
            pitchf = pitchf[:p_len]
            if "mps" not in str(self.device) and "xpu" not in str(self.device):
                pitchf = pitchf.astype(np.float32)
            pitch = torch.as_tensor(pitch, device=self.device).unsqueeze(0).long()
            pitchf = torch.as_tensor(pitchf, device=self.device).unsqueeze(0).float()
        t2 = time()
        times[1] += t2 - t1
        for t in opt_ts:
            t = t // self.window * self.window
            if if_f0:
                audio_opt.append(
                    self.vc(
                        model,
                        net_g,
                        sid,
                        audio_pad[s : t + self.t_pad2 + self.window],
                        pitch[:, s // self.window : (t + self.t_pad2) // self.window],
                        pitchf[:, s // self.window : (t + self.t_pad2) // self.window],
                        times,
                        index,
                        big_npy,
                        index_rate,
                        version,
                        protect,
                    )[self.t_pad_tgt : -self.t_pad_tgt]
                )
            else:
                audio_opt.append(
                    self.vc(
                        model,
                        net_g,
                        sid,
                        audio_pad[s : t + self.t_pad2 + self.window],
                        None,
                        None,
                        times,
                        index,
                        big_npy,
                        index_rate,
                        version,
                        protect,
                    )[self.t_pad_tgt : -self.t_pad_tgt]
                )
            s = t
        if if_f0:
            audio_opt.append(
                self.vc(
                    model,
                    net_g,
                    sid,
                    audio_pad[t:],
                    pitch[:, t // self.window :] if t is not None else pitch,
                    pitchf[:, t // self.window :] if t is not None else pitchf,
                    times,
                    index,
                    big_npy,
                    index_rate,
                    version,
                    protect,
                )[self.t_pad_tgt : -self.t_pad_tgt]
            )
        else:
            audio_opt.append(
                self.vc(
                    model,
                    net_g,
                    sid,
                    audio_pad[t:],
                    None,
                    None,
                    times,
                    index,
                    big_npy,
                    index_rate,
                    version,
                    protect,
                )[self.t_pad_tgt : -self.t_pad_tgt]
            )
        audio_opt = np.concatenate(audio_opt)
        if rms_mix_rate != 1:
            audio_opt = change_rms(audio, 16000, audio_opt, tgt_sr, rms_mix_rate)
        if tgt_sr != resample_sr >= 16000:
            audio_opt = librosa.resample(
                audio_opt, orig_sr=tgt_sr, target_sr=resample_sr
            )
        audio_max = np.abs(audio_opt).max() / 0.99
        max_int16 = 32768
        if audio_max > 1:
            max_int16 /= audio_max
        np.multiply(audio_opt, max_int16, audio_opt)
        del pitch, pitchf, sid
        return audio_opt
