# 🎬 ASMR Pro Cutter

Automatic tool to cut and create ASMR clips from long videos, with AI-based intelligent audio analysis to identify the best moments.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🎯 **Intelligent audio analysis** - Automatically detects the best ASMR triggers (clicks, taps, crunches)
- 🎨 **Modern graphical interface** - Intuitive GUI with tkinter
- ⚡ **GPU acceleration** - NVIDIA NVENC support for ultra-fast encoding
- 🎞️ **Quality preserved** - Maintains source video quality (2K/4K)
- 📊 **Customizable parameters** - Adjustable clip duration, pre/post-roll
- 🗂️ **Organized output** - Automatically saves clips with ordered timestamps

## 🎵 How it works

The program analyzes video audio using three metrics:

1. **Spectral Centroid** - Identifies sound brightness
2. **Onset Strength** - Detects trigger impact and suddenness
3. **Zero Crossing Rate** - Finds sharp metallic/plastic sounds

It combines these parameters to create a "crispness" index and automatically selects the best moments.

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- NVIDIA GPU (optional, for hardware acceleration)
- FFmpeg (automatically installed with `imageio-ffmpeg`)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/lordpba/ASMR-Pro-Cutter.git
cd ASMR-Pro-Cutter
```

2. **Create a virtual environment (recommended)**
```bash
python -m venv .venv
```

3. **Activate the virtual environment**

Windows:
```powershell
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Install dependencies**
```bash
pip install .
```
*Or for development:*
```bash
pip install -e .
```

## 🚀 Usage

### Graphical Interface (Recommended)

```bash
python gui.py
```

1. Click "Select Video" and choose your ASMR video
2. (Optional) Select a custom output folder
3. Adjust parameters if needed:
   - **Total target duration**: Total duration of combined clips (~58s for Shorts)
   - **Pre-roll**: Seconds before trigger (default 1.2s)
   - **Post-roll**: Seconds after trigger (default 1.3s)
   - **Final clip extra**: Extra seconds for last clip closing shot (default 2.0s)
4. Click "START PROCESSING"
5. Clips will be saved to `videoname_shorts/` with ordered names

### Command Line

```bash
python main.py
```

Place videos in `video_input/` and the program will automatically process all found video files.

## 📁 Output Structure

```
your_video_shorts/
├── clip_001_at_0045s.mp4
├── clip_002_at_0123s.mp4
├── clip_003_at_0189s.mp4
└── ...
```

Files are named with progressive number and timestamp for easy sorting in video editors.

## ⚙️ Advanced Parameters

You can modify directly in `main.py` or use the GUI's advanced section:

```python
TARGET_DURATION = 58.0   # Total target duration (seconds)
PRE_ROLL = 1.2          # Seconds before trigger
POST_ROLL = 1.3         # Seconds after trigger
FINAL_CLIP_EXTRA = 2.0  # Extra seconds for last clip
MIN_FREQ = 1800         # Minimum frequency for filtering (Hz)
HOP_LENGTH = 512        # Audio analysis precision
```

### GPU/Quality Parameters

In encoding code (line ~146):

- **CQ Value** (`-cq 18`): Constant quality
  - `0` = Lossless (huge files)
  - `18` = Near lossless, excellent compromise (default)
  - `23` = High quality
  - `28` = Medium quality
  
- **NVENC Preset** (`preset="slow"`):
  - `fast` = Fast, medium quality
  - `medium` = Balanced
  - `slow` = Maximum quality (default)

## 🎥 Supported Formats

- **Input**: MP4, MOV, AVI, MKV
- **Output**: MP4 (H.264 + AAC)
- **Audio**: AAC 320kbps (maximum quality for ASMR)
- **Video**: H.264 NVENC CQ18 (near lossless)

## 💡 Tips

- For 4K videos, ensure you have at least 8GB of RAM
- GPU encoding is ~10-20x faster but requires NVIDIA GPU
- Use longer pre-roll (2-3s) for videos with slow movements
- Reduce `TARGET_DURATION` for more selective clips

## 🐛 Troubleshooting

**Error "No module named 'moviepy'"**
```bash
pip install -r requirements.txt
```

**NVENC not available error**
- Automatic fallback to libx264 (CPU)
- Make sure you have updated NVIDIA drivers

**Audio not detected**
- Verify the video has an audio track
- Try lowering the `MIN_FREQ` parameter

## ☕ Support the Project

If you find this tool useful for your content creation, please consider supporting its development!

<a href="https://www.buymeacoffee.com/mariopbay" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## 🌟 Credits

If you use ASMR Pro Cutter for your videos, we'd love to see them! 
Feel free to mention **"Made with ASMR Pro Cutter"** in your video description to help others discover this tool.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.
See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 👨‍💻 Author

Created with ❤️ by **lordpba** for the ASMR community

---

**⭐ If you like this project, leave a star on GitHub!**
