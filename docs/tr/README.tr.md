<div align="center">

# Çekme Temelli Ses Dönüşümü Web Arayüzü

VITS'e dayalı kullanımı kolay bir Ses Dönüşümü çerçevesi.

[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI)

![moe](https://counter.seku.su/cmoe?name=rvc&theme=r34)

[![Licence](https://img.shields.io/github/license/fumiama/Retrieval-based-Voice-Conversion-WebUI?style=for-the-badge)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/blob/main/LICENSE)
[![Huggingface](https://img.shields.io/badge/🤗%20-Spaces-yellow.svg?style=for-the-badge)](https://huggingface.co/fumiama/RVC-Pretrained-Models/tree/main/)

[![Discord](https://img.shields.io/badge/RVC%20Geliştiricileri-Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/HcsmBBGyVk)

</div>

---

[**SSS (Sıkça Sorulan Sorular)**](<https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/wiki/SSS-(Sıkça-Sorulan-Sorular)>)

[**İngilizce**](../../README.md) | [**中文简体**](../cn/README.cn.md) | [**日本語**](../jp/README.ja.md) | [**한국어**](../kr/README.ko.md) ([**韓國語**](../kr/README.ko.han.md)) | [**Français**](../fr/README.fr.md) | [**Türkçe**](../tr/README.tr.md) | [**Português**](../pt/README.pt.md)

Burada [Demo Video'muzu](https://www.bilibili.com/video/BV1pm4y1z7Gm/) izleyebilirsiniz!

RVC Kullanarak Gerçek Zamanlı Ses Dönüşüm Yazılımı: [w-okada/voice-changer](https://github.com/w-okada/voice-changer)

> Ön eğitim modeli için veri kümesi neredeyse 50 saatlik yüksek kaliteli VCTK açık kaynak veri kümesini kullanır.

> Yüksek kaliteli lisanslı şarkı veri setleri telif hakkı ihlali olmadan kullanımınız için eklenecektir.

> Lütfen daha büyük parametrelere, daha fazla eğitim verisine sahip RVCv3'ün ön eğitimli temel modeline göz atın; daha iyi sonuçlar, değişmeyen çıkarsama hızı ve daha az eğitim verisi gerektirir.

## Özet

Bu depo aşağıdaki özelliklere sahiptir:

- Ton sızıntısını en aza indirmek için kaynak özelliğini en iyi çıkarımı kullanarak eğitim kümesi özelliği ile değiştirme;
- Kolay ve hızlı eğitim, hatta nispeten zayıf grafik kartlarında bile;
- Az miktarda veriyle bile nispeten iyi sonuçlar alın (>=10 dakika düşük gürültülü konuşma önerilir);
- Timbraları değiştirmek için model birleştirmeyi destekleme (ckpt işleme sekmesi-> ckpt birleştir);
- Kullanımı kolay Web arayüzü;
- UVR5 modelini kullanarak hızla vokalleri ve enstrümanları ayırma.
- En güçlü Yüksek tiz Ses Çıkarma Algoritması [InterSpeech2023-RMVPE](#Krediler) sessiz ses sorununu önlemek için kullanılır. En iyi sonuçları (önemli ölçüde) sağlar ve Crepe_full'den daha hızlı çalışır, hatta daha düşük kaynak tüketimi sağlar.
- AMD/Intel grafik kartları hızlandırması desteklenir.
- Intel ARC grafik kartları hızlandırması IPEX ile desteklenir.

## Ortamın Hazırlanması

Aşağıdaki komutlar, Python sürümü 3.8 veya daha yüksek olan bir ortamda çalıştırılmalıdır.

(Windows/Linux)
İlk olarak ana bağımlılıkları pip aracılığıyla kurun:

```bash
# PyTorch ile ilgili temel bağımlılıkları kurun, zaten kuruluysa atlayın
# Referans: https://pytorch.org/get-started/locally/
pip install torch torchvision torchaudio

# Windows + Nvidia Ampere Mimarisi(RTX30xx) için, https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/issues/21 deneyime göre pytorch'a karşılık gelen cuda sürümünü belirtmeniz gerekebilir
#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
```

Sonra poetry kullanarak diğer bağımlılıkları kurabilirsiniz:

```bash
# Poetry bağımlılık yönetim aracını kurun, zaten kuruluysa atlayın
# Referans: https://python-poetry.org/docs/#installation
curl -sSL https://install.python-poetry.org | python3 -

# Projeyi bağımlılıkları kurun
poetry install
```

Ayrıca bunları pip kullanarak da kurabilirsiniz:

```bash

Nvidia grafik kartları için
  pip install -r requirements/main.txt

AMD/Intel grafik kartları için：
  pip install -r requirements/dml.txt

Intel ARC grafik kartları için Linux / WSL ile Python 3.10 kullanarak:
  pip install -r requirements/ipex.txt

```

---

Mac kullanıcıları `run.sh` aracılığıyla bağımlılıkları kurabilir:

```bash
sh ./run.sh
```

## Diğer Ön Modellerin Hazırlanması

RVC'nin çıkarım ve eğitim yapması için diğer ön modellere ihtiyacı vardır.

Bu ön modelleri [Huggingface alanımızdan](https://huggingface.co/fumiama/RVC-Pretrained-Models/tree/main/) indirmeniz gerekecektir.

İşte RVC'nin ihtiyaç duyduğu diğer ön modellerin ve dosyaların bir listesi:

```bash
./assets/hubert/hubert_base.pt

./assets/pretrained

./assets/uvr5_weights

V2 sürümü modelini test etmek isterseniz, ek özellikler indirmeniz gerekecektir.

./assets/pretrained_v2

V2 sürüm modelini test etmek isterseniz (v2 sürüm modeli, 9 katmanlı Hubert+final_proj'ün 256 boyutlu özelliğini 12 katmanlı Hubert'ün 768 boyutlu özelliğiyle değiştirmiştir ve 3 periyot ayırıcı eklemiştir), ek özellikleri indirmeniz gerekecektir.

./assets/pretrained_v2

En son SOTA RMVPE vokal ton çıkarma algoritmasını kullanmak istiyorsanız, RMVPE ağırlıklarını indirip RVC kök dizinine koymalısınız.

https://huggingface.co/fumiama/RVC-Pretrained-Models/blob/main/rmvpe/rmvpe.pt

    AMD/Intel grafik kartları kullanıcıları için indirmeniz gereken:

    https://huggingface.co/fumiama/RVC-Pretrained-Models/blob/main/rmvpe/rmvpe.onnx

```

Intel ARC grafik kartları kullanıcıları Webui'yi başlatmadan önce `source /opt/intel/oneapi/setvars.sh` komutunu çalıştırmalı.

Daha sonra bu komutu kullanarak Webui'yi başlatabilirsiniz:

```bash
python web.py
```

Windows veya macOS kullanıyorsanız, `RVC-beta.7z` dosyasını indirip çıkararak `go-web.bat`i kullanarak veya macOS'ta `sh ./run.sh` kullanarak doğrudan RVC'yi kullanabilirsiniz.

## Krediler

- [ContentVec](https://github.com/auspicious3000/contentvec/)
- [VITS](https://github.com/jaywalnut310/vits)
- [HIFIGAN](https://github.com/jik876/hifi-gan)
- [Gradio](https://github.com/gradio-app/gradio)
- [Ultimate Vocal Remover](https://github.com/Anjok07/ultimatevocalremovergui)
- [audio-slicer](https://github.com/openvpi/audio-slicer)
- [Vokal ton çıkarma:RMVPE](https://github.com/Dream-High/RMVPE)
  - Ön eğitimli model [yxlllc](https://github.com/yxlllc/RMVPE) ve [RVC-Boss](https://github.com/RVC-Boss) tarafından eğitilip test edilmiştir.

## Katkıda Bulunan Herkese Teşekkürler

[![contributors](https://contrib.rocks/image?repo=fumiama/Retrieval-based-Voice-Conversion-WebUI)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/graphs/contributors)

```

```
