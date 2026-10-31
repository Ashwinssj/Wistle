# 🎤 Whistle Assistant — Offline Voice Assistant

A Siri-like voice assistant that runs **entirely offline** on your device. Uses [Whistle](https://huggingface.co/Cactus-Compute/whistle) (16.9 MB) for speech-to-text and [Needle 3](https://huggingface.co/Cactus-Compute/needle3) for tool calling. No cloud, no API keys, no internet required after initial model download.

## ✨ Features

- **🎯 Wake word activation** — "Hey Assistant", "Okay Assistant", "Whistle", "Computer"
- **🗣️ Speech-to-text** — Whistle ASR (7 languages, 16.9 MB model)
- **🛠️ Tool calling** — Needle 3 understands intent and executes actions
- **📱 Cross-platform** — Windows, Linux, macOS, Android, iOS
- **🔒 100% offline** — Models cached locally, no data leaves your device
- **⚡ Fast** — Runs on CPU, no GPU needed

## 🛠️ Built-in Actions

| Action | Example Commands |
|--------|------------------|
| **Open apps** | "Open Chrome", "Launch VS Code", "Start Calculator" |
| **Set reminders** | "Remind me to call mom in 10 minutes", "Set reminder for 3 PM" |
| **List reminders** | "What are my reminders?" |
| **Search files** | "Find files about project alpha", "Search for budget spreadsheet" |
| **Open files** | "Open the budget spreadsheet" |
| **Get time** | "What time is it?", "What's today's date?" |
| **Run commands** | "Run dir", "Execute ls -la" |

---

## 💻 PC Install (Windows / Linux / macOS)

### Prerequisites
- Python 3.10+
- Microphone
- ~500 MB disk space (models + dependencies)

### Quick Install

```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/whistle-assistant
cd whistle-assistant

# 2. Create virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 3. Install with microphone support
pip install -e ".[mic]"

# 4. Run! (Downloads models on first run ~50 MB)
whistle-assistant
```

### Windows-Specific Notes

```powershell
# If you get audio device errors, list devices first:
whistle-assistant --list-devices

# Then specify your microphone:
whistle-assistant --device 1
```

### Linux-Specific Notes

```bash
# Install system audio dependencies
# Ubuntu/Debian:
sudo apt install portaudio19-dev python3-pyaudio

# Arch:
sudo pacman -S portaudio python-pyaudio

# Fedora:
sudo dnf install portaudio-devel python3-pyaudio
```

### macOS-Specific Notes

```bash
# Install portaudio
brew install portaudio

# May need to grant microphone permission in System Settings → Privacy & Security → Microphone
```

---

## 📱 Phone Install (Android / iOS)

### Option A: Kivy App (Android — Recommended)

The assistant includes a Kivy-based mobile UI. Build with Buildozer:

```bash
# 1. Install buildozer (Linux/WSL only)
pip install buildozer

# 2. Install Android build dependencies (Ubuntu/WSL)
sudo apt update && sudo apt install -y \
    git zip unzip openjdk-17-jdk python3-pip autoconf libtool \
    pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev automake

# 3. Configure buildozer.spec (already included)
# Edit buildozer.spec if needed

# 4. Build debug APK
buildozer -v android debug

# 5. Install on device
adb install bin/whistleassistant-0.1.0-armeabi-v7a-debug.apk
```

**buildozer.spec** (included in repo):
```ini
[app]
title = Whistle Assistant
package.name = whistleassistant
package.domain = org.example
source.dir = src
source.include_exts = py,png,jpg,kv,atlas,yaml
version = 0.1.0
requirements = python3,kivy,cactus-needle[mic],numpy,plyer,pyyaml,psutil,watchdog
orientation = portrait
android.permissions = RECORD_AUDIO,INTERNET,FOREGROUND_SERVICE,WAKE_LOCK
android.features = android.hardware.microphone
android.api = 34
android.minapi = 24
android.sdk = 34
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
```

### Option B: Native Python (Android with Termux)

```bash
# In Termux:
pkg install python python-pip portaudio binutils
pip install cactus-needle[mic] numpy sounddevice pyyaml psutil watchdog plyer

# Run
whistle-assistant
```

### Option C: iOS (Experimental)

Requires Xcode and rubicon-objc. The Python package works but needs a Swift UI wrapper:

```bash
# On macOS with Xcode:
pip install rubicon-objc
# Then build a simple SwiftUI app that calls the Python backend via PyObjC or subprocess
```

---

## ⚙️ Configuration

Copy `config.yaml` to your config directory:

```bash
# Linux/macOS:
mkdir -p ~/.config/whistle-assistant
cp config.yaml ~/.config/whistle-assistant/

# Windows:
mkdir %APPDATA%\whistle-assistant
copy config.yaml %APPDATA%\whistle-assistant\
```

### Key Settings

```yaml
wake_words:
  - "hey assistant"
  - "okay assistant"
  - "whistle"

audio:
  input_device: null  # Run with --list-devices to find yours

asr:
  language: null      # null = auto-detect
  keywords: []        # Add names/terms for better recognition

tools:
  app_aliases:
    browser: ["chrome", "edge", "firefox"]
    terminal: ["cmd", "powershell", "terminal"]
```

---

## 🎮 Usage

### Basic Commands

```
You: "Hey Assistant"
Assistant: *beep* "Listening..."

You: "Open Chrome"
Assistant: "Opened Chrome"

You: "Remind me to take a break in 20 minutes"
Assistant: "Reminder set for 14:35: Take a break"

You: "Find files about machine learning"
Assistant: "Found 3 files: ml-notes.md, paper.pdf, dataset.csv"

You: "What time is it?"
Assistant: "It's 2:15 PM on Friday, January 17, 2025"
```

### Advanced Examples

```
"Set a reminder for 9 AM tomorrow to review the PR"
"Search for Python files modified this week"
"Open the downloads folder"
"Run python test.py"
"Cancel my 3 PM reminder"
```

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Microphone    │────▶│   Whistle ASR   │────▶│   Needle 3      │
│   (16 kHz)      │     │   (16.9 MB)     │     │   Tool Calling  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                        ┌─────────────────┐               │
                        │   Text-to-Speech│◀──────────────┘
                        │   (System TTS)  │
                        └─────────────────┘
```

**Models** (downloaded on first run, cached locally):
- `whistle.cact` — 16.9 MB speech-to-text
- `needle3.cact` — ~35 MB tool-calling model
- Engine libraries — < 1 MB each (platform-specific)

---

## 🔧 Development

### Project Structure

```
whistle-assistant/
├── src/whistle_assistant/
│   ├── __init__.py       # Main assistant logic
│   └── __main__.py       # CLI entry point
├── config.yaml           # Default configuration
├── pyproject.toml        # Package metadata
├── buildozer.spec        # Android build config
└── README.md
```

### Adding Custom Tools

```python
# In your own script:
import needle
from whistle_assistant import VoiceAssistant

@needle.tool
def my_custom_tool(param: str) -> dict:
    """Description for the model."""
    return {"success": True, "message": f"Did something with {param}"}

assistant = VoiceAssistant()
assistant.agent._functions["my_custom_tool"] = my_custom_tool
# Add to Needle's tool schema...
assistant.run_forever()
```

### Running Tests

```bash
pytest tests/
```

---

## 📦 Model Details

| Model | Size | Languages | License |
|-------|------|-----------|---------|
| Whistle | 16.9 MB | EN, DE, FR, ES, IT, NL, PL | Apache-2.0 |
| Needle 3 | ~35 MB | Tool calling (any) | Apache-2.0 |

Both models use Cactus Quants 2-bit quantization and run on the same C++ engine.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No audio input device" | Run `--list-devices`, then `--device N` |
| "Model download failed" | Check internet, retry; models cache in `~/.cache/cactus-needle/` |
| High CPU usage | Reduce `chunk_duration` in config |
| Wake word not detected | Lower `silence_threshold`, add keywords |
| TTS not working | Install `espeak` (Linux), check Windows Speech Platform |

---

## 📄 License

Apache-2.0 — Same as Whistle and Needle models.

## 🙏 Credits

- [Cactus Compute](https://cactuscompute.com) — Whistle & Needle models
- [cactus-needle](https://github.com/cactus-compute/needle) — Python bindings

---

## 🤝 Contributing

PRs welcome! Areas for improvement:
- More tools (calendar, email, smart home)
- Better wake word detection (custom KWS model)
- Persistent reminder storage
- Mobile UI polish
- Plugin system for custom tools