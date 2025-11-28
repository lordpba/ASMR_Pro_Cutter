# 🎬 ASMR Pro Cutter

Strumento automatico per tagliare e creare clip ASMR da video lunghi, con analisi audio intelligente basata su AI per identificare i momenti migliori.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Caratteristiche

- 🎯 **Analisi audio intelligente** - Rileva automaticamente i migliori trigger ASMR (click, tap, crunch)
- 🎨 **Interfaccia grafica moderna** - GUI intuitiva con tkinter
- ⚡ **Accelerazione GPU** - Supporto NVIDIA NVENC per encoding ultra-rapido
- 🎞️ **Qualità preservata** - Mantiene la qualità del video sorgente (2K/4K)
- 📊 **Parametri personalizzabili** - Durata clip, pre/post-roll regolabili
- 🗂️ **Output organizzato** - Salva automaticamente clip con timestamp ordinati

## 🎵 Come funziona

Il programma analizza l'audio del video usando tre metriche:

1. **Spectral Centroid** - Identifica la brillantezza dei suoni
2. **Onset Strength** - Rileva l'impatto e l'improvvisità dei trigger
3. **Zero Crossing Rate** - Trova suoni acuti metallici/plastici

Combina questi parametri per creare un indice di "croccantezza" (crispness) e seleziona automaticamente i momenti migliori.

## 📦 Installazione

### Prerequisiti

- Python 3.8 o superiore
- GPU NVIDIA (opzionale, per accelerazione hardware)
- FFmpeg (installato automaticamente con `imageio-ffmpeg`)

### Setup

1. **Clona il repository**
```bash
git clone https://github.com/tuousername/ASMR-Pro-Cutter.git
cd ASMR-Pro-Cutter
```

2. **Crea un ambiente virtuale (consigliato)**
```bash
python -m venv .venv
```

3. **Attiva l'ambiente virtuale**

Windows:
```powershell
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

## 🚀 Utilizzo

### Interfaccia Grafica (Consigliato)

```bash
python gui.py
```

1. Clicca su "Seleziona Video" e scegli il tuo video ASMR
2. (Opzionale) Seleziona una cartella di output personalizzata
3. Regola i parametri se necessario:
   - **Durata totale target**: Durata totale dei clip combinati (~58s per Shorts)
   - **Pre-roll**: Secondi prima del trigger (default 1.2s)
   - **Post-roll**: Secondi dopo il trigger (default 1.3s)
4. Clicca "AVVIA PROCESSING"
5. I clip verranno salvati in `nomevideo_shorts/` con nomi ordinati

### Linea di Comando

```bash
python main.py
```

Metti i video in `video_input/` e il programma processerà automaticamente tutti i file video trovati.

## 📁 Struttura Output

```
tuo_video_shorts/
├── clip_001_at_0045s.mp4
├── clip_002_at_0123s.mp4
├── clip_003_at_0189s.mp4
└── ...
```

I file sono nominati con numero progressivo e timestamp per facile ordinamento negli editor video.

## ⚙️ Parametri Avanzati

Puoi modificare direttamente in `main.py`:

```python
TARGET_DURATION = 58.0   # Durata totale target (secondi)
PRE_ROLL = 1.2          # Secondi prima del trigger
POST_ROLL = 1.3         # Secondi dopo del trigger
MIN_FREQ = 1800         # Frequenza minima per filtraggio (Hz)
```

### Parametri GPU/Qualità

Nel codice di encoding (linea ~146):

- **CQ Value** (`-cq 18`): Qualità costante
  - `0` = Lossless (file enormi)
  - `18` = Quasi lossless, ottimo compromesso (default)
  - `23` = Alta qualità
  - `28` = Media qualità
  
- **Preset NVENC** (`preset="slow"`):
  - `fast` = Veloce, qualità media
  - `medium` = Bilanciato
  - `slow` = Massima qualità (default)

## 🎥 Formati Supportati

- **Input**: MP4, MOV, AVI, MKV
- **Output**: MP4 (H.264 + AAC)
- **Audio**: AAC 320kbps (massima qualità per ASMR)
- **Video**: H.264 NVENC CQ18 (quasi lossless)

## 💡 Consigli

- Per video 4K, assicurati di avere almeno 8GB di RAM
- L'encoding GPU è ~10-20x più veloce ma richiede NVIDIA GPU
- Usa pre-roll più lungo (2-3s) per video con movimenti lenti
- Riduci `TARGET_DURATION` per clip più selettivi

## 🐛 Troubleshooting

**Errore "No module named 'moviepy'"**
```bash
pip install -r requirements.txt
```

**Errore NVENC non disponibile**
- Fallback automatico su libx264 (CPU)
- Assicurati di avere driver NVIDIA aggiornati

**Audio non rilevato**
- Verifica che il video abbia traccia audio
- Prova ad abbassare il parametro `MIN_FREQ`

## 📄 Licenza

MIT License - Vedi [LICENSE](LICENSE) per dettagli

## 🤝 Contributi

Pull request benvenute! Per modifiche importanti, apri prima un'issue.

## 👨‍💻 Autore

Creato con ❤️ per la community ASMR

---

**⭐ Se ti piace questo progetto, lascia una stella su GitHub!**
