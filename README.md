<div align="center">

# Retrieval-based-Voice-Conversion-WebUI

An easy-to-use voice conversion framework based on VITS.

[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI)

![moe](https://counter.seku.su/cmoe?name=rvc&theme=r34)

[![Licence](https://img.shields.io/github/license/fumiama/Retrieval-based-Voice-Conversion-WebUI?style=for-the-badge)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/blob/main/LICENSE)
[![Huggingface](https://img.shields.io/badge/🤗%20-Spaces-yellow.svg?style=for-the-badge)](https://huggingface.co/fumiama/RVC-Pretrained-Models/tree/main/)

[![Discord](https://img.shields.io/badge/RVC%20Developers-Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/HcsmBBGyVk)

[**FAQ (Frequently Asked Questions)**](<https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/wiki/FAQ-(Frequently-Asked-Questions)>)

[**English**](./README.md) | [**中文简体**](./docs/cn/README.cn.md) | [**日本語**](./docs/jp/README.ja.md) | [**한국어**](./docs/kr/README.ko.md) ([**韓國語**](./docs/kr/README.ko.han.md)) | [**Français**](./docs/fr/README.fr.md) | [**Türkçe**](./docs/tr/README.tr.md) | [**Português**](./docs/pt/README.pt.md)

</div>

> The base model is trained using nearly 50 hours of high-quality open-source VCTK training set. Therefore, there are no copyright concerns, please feel free to use.

> Please look forward to the base model of RVCv3 with larger parameters, larger dataset, better effects, basically flat inference speed, and less training data required.

> There's a [one-click downloader](https://github.com/fumiama/RVC-Models-Downloader) for models/integration packages/tools. Welcome to try.

|                                                  Training and inference Webui                                                  |
| :----------------------------------------------------------------------------------------------------------------------------: |
| ![web](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/assets/41315874/17e48404-2627-4fad-a0ec-65f9065aeade) |

|                                                      Real-time voice changing GUI                                                       |
| :-------------------------------------------------------------------------------------------------------------------------------------: |
| ![realtime-gui](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/assets/41315874/95b36866-b92d-40c7-b5db-6a35ca5caeac) |

## Features:

- Reduce tone leakage by replacing the source feature to training-set feature using top1 retrieval;
- Easy + fast training, even on poor graphics cards;
- Training with a small amounts of data (>=10min low noise speech recommended);
- Model fusion to change timbres (using ckpt processing tab->ckpt merge);
- Easy-to-use WebUI;
- UVR5 model to quickly separate vocals and instruments;
- High-pitch Voice Extraction Algorithm [InterSpeech2023-RMVPE](#Credits) to prevent a muted sound problem. Provides the best results (significantly) and is faster with lower resource consumption than Crepe_full;
- Nvidia CUDA, AMD ROCm, and Windows DirectML acceleration supported.

Check out our [Demo Video](https://www.bilibili.com/video/BV1pm4y1z7Gm/) here!

## Environment Configuration

### Python Version Limitation

> It is recommended to use `uv` or `venv` to manage the Python environment.

> Python 3.12 is recommended.

> For the reason of the version limitation, please refer to this [bug](https://github.com/facebookresearch/fairseq/issues/5012).

```bash
python --version # Recommend: 3.12
```

### Recommended Dependency Installation with uv

Install `uv` first:

```bash
python -m pip install -U uv
```

Create the virtual environment:

```bash
uv venv --python 3.12
```

Activate it:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the dependency set matching your hardware:

```bash
uv sync --extra cuda
```

For CPU:

```bash
uv sync --extra cpu
```

For AMD ROCm on Linux:

```bash
uv sync --extra rocm
```

For AMD/Intel DirectML on Windows:

```bash
uv sync --extra dml
```

For real-time GUI features, add the `gui` extra:

```bash
uv sync --extra cuda --extra gui
```

or, for DirectML GUI:

```bash
uv sync --extra dml --extra gui
```

### Linux/MacOS One-click Dependency Installation & Startup Script

By executing `run.sh` in the project root directory, you can configure the `venv` virtual environment, automatically install the required dependencies, and start the main program with one click.

```bash
sh ./run.sh
```

### Manual PyTorch Installation Reference

`uv sync` is the recommended installation path. For manual installations, install PyTorch using the wheel index matching your hardware before installing the remaining dependencies.

CPU:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

Nvidia GPU:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

AMD ROCm on Linux:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```

AMD/Intel DirectML on Windows:

```bash
pip install torch-directml torchvision torchaudio
```

## Preparation of Other Files

### 1. Assets

> RVC requires some models located in the `assets` folder for inference and training.

#### Check/Download Automatically (Default)

> By default, RVC can automatically check the integrity of the required resources when the main program starts.

> Even if the resources are not complete, the program will continue to start.

- If you want to download all resources, please add the `--update` parameter.
- If you want to skip the resource integrity check at startup, please add the `--nocheck` parameter.

#### Download Manually

> All resource files are located in [Hugging Face space](https://huggingface.co/fumiama/RVC-Pretrained-Models/tree/main/)

> You can find some scripts to download them in the `tools` folder

> You can also use the [one-click downloader](https://github.com/fumiama/RVC-Models-Downloader) for models/integration packages/tools

Below is a list that includes the names of all pre-models and other files required by RVC.

- ./assets/hubert/hubert_base.pt

  ```bash
  rvcmd assets/hubert # RVC-Models-Downloader command
  ```

- ./assets/pretrained

  ```bash
  rvcmd assets/v1 # RVC-Models-Downloader command
  ```

- ./assets/uvr5_weights

  ```bash
  rvcmd assets/uvr5 # RVC-Models-Downloader command
  ```

If you want to use the v2 version of the model, you need to download additional resources in

- ./assets/pretrained_v2

  ```bash
  rvcmd assets/v2 # RVC-Models-Downloader command
  ```

### 2. Download the required files for the rmvpe vocal pitch extraction algorithm

If you want to use the latest RMVPE vocal pitch extraction algorithm, you need to download the pitch extraction model parameters and place them in `assets/rmvpe`.

- [rmvpe.pt](https://huggingface.co/fumiama/RVC-Pretrained-Models/blob/main/rmvpe/rmvpe.pt)

  ```bash
  rvcmd assets/rmvpe # RVC-Models-Downloader command
  ```

#### Download DML environment of RMVPE (optional, for AMD/Intel GPU)

- [rmvpe.onnx](https://huggingface.co/fumiama/RVC-Pretrained-Models/blob/main/rmvpe/rmvpe.onnx)

  ```bash
  rvcmd assets/rmvpe # RVC-Models-Downloader command
  ```

### 3. AMD ROCm (optional, Linux only)

If you want to run RVC on a Linux system based on AMD's ROCm technology, please first install the required drivers [here](https://rocm.docs.amd.com/en/latest/deploy/linux/os-native/install.html).

If you are using Arch Linux, you can use pacman to install the required drivers.

```bash
pacman -S rocm-hip-sdk rocm-opencl-sdk
```

For some models of graphics cards, you may need to configure the following environment variables, such as RX6700XT.

```bash
export ROCM_PATH=/opt/rocm # Set ROCm executables path
export HSA_OVERRIDE_GFX_VERSION=10.3.0 # Spoof GPU model for ROCm
```

Also, make sure your current user is in the `render` and `video` user groups.

```bash
sudo usermod -aG render $USERNAME
sudo usermod -aG video $USERNAME
```

## Getting Started

### Direct Launch

Use the following command to start the WebUI.

```bash
python web.py
```

When using `uv`, you can also launch through the managed environment:

```bash
uv run python web.py
```

### Linux/MacOS

```bash
./run.sh
```

### Using the Integration Package (Windows Users)

Download and unzip `RVC-beta.7z`. After unzipping, double-click `go-web.bat` to start the program with one click.

```bash
rvcmd packs/general/latest # RVC-Models-Downloader command
```

## Credits

- [ContentVec](https://github.com/auspicious3000/contentvec/)
- [VITS](https://github.com/jaywalnut310/vits)
- [HIFIGAN](https://github.com/jik876/hifi-gan)
- [Gradio](https://github.com/gradio-app/gradio)
- [Ultimate Vocal Remover](https://github.com/Anjok07/ultimatevocalremovergui)
- [audio-slicer](https://github.com/openvpi/audio-slicer)
- [Vocal pitch extraction:RMVPE](https://github.com/Dream-High/RMVPE)
  - The pretrained model is trained and tested by [yxlllc](https://github.com/yxlllc/RMVPE) and [RVC-Boss](https://github.com/RVC-Boss).

## Thanks to all contributors for their efforts

[![contributors](https://contrib.rocks/image?repo=fumiama/Retrieval-based-Voice-Conversion-WebUI)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/graphs/contributors)
