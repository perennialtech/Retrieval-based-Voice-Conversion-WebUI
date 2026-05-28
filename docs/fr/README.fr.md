<div align="center">

# Retrieval-based-Voice-Conversion-WebUI

Un framework simple et facile à utiliser pour la conversion vocale (modificateur de voix) basé sur VITS

[![madewithlove](https://img.shields.io/badge/made_with-%E2%9D%A4-red?style=for-the-badge&labelColor=orange)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI)

![moe](https://counter.seku.su/cmoe?name=rvc&theme=r34)

[![Licence](https://img.shields.io/github/license/fumiama/Retrieval-based-Voice-Conversion-WebUI?style=for-the-badge)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/blob/main/LICENSE)
[![Huggingface](https://img.shields.io/badge/🤗%20-Spaces-yellow.svg?style=for-the-badge)](https://huggingface.co/fumiama/RVC-Pretrained-Models/tree/main/)

[![Discord](https://img.shields.io/badge/RVC%20Developers-Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/HcsmBBGyVk)

[**FAQ**](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98%E8%A7%A3%E7%AD%94) | [**AutoDL·Formation d'un chanteur AI pour 5 centimes**](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/wiki/Autodl%E8%AE%AD%E7%BB%83RVC%C2%B7AI%E6%AD%8C%E6%89%8B%E6%95%99%E7%A8%8B) | [**Enregistrement des expériences comparatives**](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/wiki/%E5%AF%B9%E7%85%A7%E5%AE%9E%E9%AA%8C%C2%B7%E5%AE%9E%E9%AA%8C%E8%AE%B0%E5%BD%95) | [**Démonstration en ligne**](https://huggingface.co/spaces/Ricecake123/RVC-demo)

</div>

---

[**English**](../../README.md) | [ **中文简体**](../cn/README.cn.md) | [**日本語**](../jp/README.ja.md) | [**한국어**](../kr/README.ko.md) ([**韓國語**](../kr/README.ko.han.md)) | [**Français**](../fr/README.fr.md) | [**Turc**](../tr/README.tr.md) | [**Português**](../pt/README.pt.md)

Cliquez ici pour voir notre [vidéo de démonstration](https://www.bilibili.com/video/BV1pm4y1z7Gm/) !

> Conversion vocale en temps réel avec RVC : [w-okada/voice-changer](https://github.com/w-okada/voice-changer)

> Le modèle de base est formé avec près de 50 heures de données VCTK de haute qualité et open source. Aucun souci concernant les droits d'auteur, n'hésitez pas à l'utiliser.

> Attendez-vous au modèle de base RVCv3 : plus de paramètres, plus de données, de meilleurs résultats, une vitesse d'inférence presque identique, et nécessite moins de données pour la formation.

## Introduction

Ce dépôt a les caractéristiques suivantes :

- Utilise le top1 pour remplacer les caractéristiques de la source d'entrée par les caractéristiques de l'ensemble d'entraînement pour éliminer les fuites de timbre vocal.
- Peut être formé rapidement même sur une carte graphique relativement moins performante.
- Obtient de bons résultats même avec peu de données pour la formation (il est recommandé de collecter au moins 10 minutes de données vocales avec un faible bruit de fond).
- Peut changer le timbre vocal en fusionnant des modèles (avec l'aide de l'onglet ckpt-merge).
- Interface web simple et facile à utiliser.
- Peut appeler le modèle UVR5 pour séparer rapidement la voix et l'accompagnement.
- Utilise l'algorithme de pitch vocal le plus avancé [InterSpeech2023-RMVPE](#projets-référencés) pour éliminer les problèmes de voix muette. Meilleurs résultats, plus rapide que crepe_full, et moins gourmand en ressources.
- Support d'accélération pour les cartes AMD et Intel.

## Configuration de l'environnement

Exécutez les commandes suivantes dans un environnement Python de version 3.8 ou supérieure.

(Windows/Linux)  
Installez d'abord les dépendances principales via pip :

```bash
# Installez Pytorch et ses dépendances essentielles, sautez si déjà installé.
# Voir : https://pytorch.org/get-started/locally/
pip install torch torchvision torchaudio

# Pour les utilisateurs de Windows avec une architecture Nvidia Ampere (RTX30xx), en se basant sur l'expérience #21, spécifiez la version CUDA correspondante pour Pytorch.
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

# Pour Linux + carte AMD, utilisez cette version de Pytorch:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```

Vous pouvez utiliser poetry pour installer les dépendances :

```bash
# Installez l'outil de gestion des dépendances Poetry, sautez si déjà installé.
# Voir : https://python-poetry.org/docs/#installation
curl -sSL https://install.python-poetry.org | python3 -

# Installez les dépendances avec poetry.
poetry install
```

Ou vous pouvez utiliser pip pour installer les dépendances :

```bash
# Cartes Nvidia :
pip install -r requirements/main.txt

# Cartes AMD/Intel :
pip install -r requirements/dml.txt

# Cartes Intel avec IPEX
pip install -r requirements/ipex.txt

# Cartes AMD sur Linux (ROCm)
pip install -r requirements/amd.txt
```

---

Les utilisateurs de Mac peuvent exécuter `run.sh` pour installer les dépendances :

```bash
sh ./run.sh
```

## Préparation d'autres modèles pré-entraînés

RVC nécessite d'autres modèles pré-entraînés pour l'inférence et la formation.

```bash
python tools/download_models.py
```

Ou vous pouvez télécharger ces modèles depuis notre [espace Hugging Face](https://huggingface.co/fumiama/RVC-Pretrained-Models/tree/main/).

Voici une liste des modèles et autres fichiers requis par RVC :

```bash
./assets/hubert/hubert_base.pt

./assets/pretrained

./assets/uvr5_weights

# Pour tester la version v2 du modèle, téléchargez également :

./assets/pretrained_v2

# Si vous souhaitez utiliser le dernier algorithme RMVPE de pitch vocal, téléchargez les paramètres du modèle de pitch et placez-les dans le répertoire racine de RVC.

https://huggingface.co/fumiama/RVC-Pretrained-Models/blob/main/rmvpe/rmvpe.pt

    # Les utilisateurs de cartes AMD/Intel nécessitant l'environnement DML doivent télécharger :

    https://huggingface.co/fumiama/RVC-Pretrained-Models/blob/main/rmvpe/rmvpe.onnx

```

Pour les utilisateurs d'Intel ARC avec IPEX, exécutez d'abord `source /opt/intel/oneapi/setvars.sh`.
Ensuite, exécutez la commande suivante pour démarrer WebUI :

```bash
python web.py
```

Si vous utilisez Windows ou macOS, vous pouvez télécharger et extraire `RVC-beta.7z`. Les utilisateurs de Windows peuvent exécuter `go-web.bat` pour démarrer WebUI, tandis que les utilisateurs de macOS peuvent exécuter `sh ./run.sh`.

## Compatibilité ROCm pour les cartes AMD (seulement Linux)

Installez tous les pilotes décrits [ici](https://rocm.docs.amd.com/en/latest/deploy/linux/os-native/install.html).

Sur Arch utilisez pacman pour installer le pilote:

```
pacman -S rocm-hip-sdk rocm-opencl-sdk
```

Vous devrez peut-être créer ces variables d'environnement (par exemple avec RX6700XT):

```
export ROCM_PATH=/opt/rocm
export HSA_OVERRIDE_GFX_VERSION=10.3.0
```

Et remplacer PyTorch par sa version ROCM après l'installation des dépendances.

```
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
```

Assurez-vous que votre utilisateur est dans les groupes `render` et `video`:

```
sudo usermod -aG render $USERNAME
sudo usermod -aG video $USERNAME
```

Enfin vous pouvez exécuter WebUI:

```bash
python web.py
```

## Crédits

- [ContentVec](https://github.com/auspicious3000/contentvec/)
- [VITS](https://github.com/jaywalnut310/vits)
- [HIFIGAN](https://github.com/jik876/hifi-gan)
- [Gradio](https://github.com/gradio-app/gradio)
- [Ultimate Vocal Remover](https://github.com/Anjok07/ultimatevocalremovergui)
- [audio-slicer](https://github.com/openvpi/audio-slicer)
- [Extraction de la hauteur vocale : RMVPE](https://github.com/Dream-High/RMVPE)
  - Le modèle pré-entraîné a été formé et testé par [yxlllc](https://github.com/yxlllc/RMVPE) et [RVC-Boss](https://github.com/RVC-Boss).

## Remerciements à tous les contributeurs pour leurs efforts

[![contributors](https://contrib.rocks/image?repo=fumiama/Retrieval-based-Voice-Conversion-WebUI)](https://github.com/fumiama/Retrieval-based-Voice-Conversion-WebUI/graphs/contributors)
