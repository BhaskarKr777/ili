<div align="center">

<h1>ili — Interactive Learning Intelligence</h1>

<img src="/banner.png" alt="ili Logo" width="40%" style="opacity:0.5;" />

<p>
  <strong>
    An open-source, offline-first AI tutor with voice, animated avatar, and persistent memory.
  </strong>
</p>

<p>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  </a>
  <a href="https://ollama.ai">
    <img src="https://img.shields.io/badge/Powered%20by-Ollama-black.svg" alt="Powered by Ollama">
  </a>
  <a href="CONTRIBUTING.md">
    <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
  </a>
</p>

<p>
  <a href="#features">Features</a> •
  <a href="#demo">Demo</a> •
  <a href="#installation">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#faq">FAQ</a>
</p>

</div>

---



## What is ili?

**ili** (Interactive Learning Intelligence) is a modular, offline-first AI tutoring platform. It runs entirely on your machine — no cloud required — and gives you a personal AI tutor with:

- 🧠 **Smart tutoring** powered by local LLMs (via Ollama) or cloud APIs (OpenAI, Gemini)
- 🎙️ **Voice I/O** — speak your questions, hear answers (fully offline)
- 🧑‍🎨 **Animated avatar** — reacts with gestures based on context
- 💾 **Persistent memory** — remembers your learning sessions across days
- 🔌 **Pluggable engines** — swap LLMs without changing anything else

---

## Demo

> 📸 _Screenshots and demo GIF coming soon — contributors welcome!_

```
👋 Welcome back, Student!

📚 Previous sessions:
  [0] Start a new session
  [1] 2026-02-28 12:30  |  local  |  5 exchanges  |  math, physics

You: explain gravity in simple terms
🤖 Tutor: Gravity is like an invisible friendship between objects...
         [avatar switches to pointing gesture, speaks response aloud]
```

---

## Features

| Feature | Status |
|---|---|
| Local LLM (Ollama) | ✅ Ready |
| OpenAI GPT engine | ✅ Ready |
| Google Gemini engine | ✅ Ready |
| Offline voice output (Piper TTS) | ✅ Ready |
| Offline voice input (whisper.cpp) | ✅ Ready |
| Animated pygame avatar | ✅ Ready |
| Context-based gestures | ✅ Ready |
| Persistent session memory | ✅ Ready |
| Subject modes (Math, Science...) | 🔜 Roadmap |
| Web UI | 🔜 Roadmap |
| Mobile app | 🔜 Roadmap |

---

## Installation

### Requirements

- Python 3.10 or higher
- Windows 10/11 (Linux/macOS support planned)
- 4GB+ RAM (8GB recommended)
- GPU optional but recommended for local LLMs

### Step 1 — Clone the repo

```bash
git clone https://github.com/yourusername/ili.git
cd ili
```

### Step 2 — Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set up local LLM (recommended)

Install [Ollama](https://ollama.ai) then pull a model:

```bash
ollama pull phi3.5       # 2.2GB — recommended for 4GB VRAM
ollama pull llama3.2     # 2GB   — faster, good quality
ollama pull mistral      # 4GB   — best quality, needs more VRAM
```

### Step 5 — Set up voice output (optional)

Download and place in `voice/piper/`:
- [piper.exe](https://github.com/rhasspy/piper/releases/latest) — extract `piper_windows_amd64.zip`
- [en_US-lessac-medium.onnx](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium) — voice model

### Step 6 — Set up voice input (optional)

Download and place in `voice/whisper/`:
- [whisper-cli.exe](https://github.com/ggerganov/whisper.cpp/releases/latest) — from `whisper-bin-x64.zip`
- [ggml-small.bin](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin) — place in `voice/whisper/models/`

### Step 7 — Set up avatar images (optional)

Generate 9 character images using any AI art tool and place in `avatar/assets/`:

```
avatar/assets/
├── idle.png
├── idle_breathe.png
├── talking_1.png
├── talking_2.png
├── thinking.png
├── happy.png
├── confused.png
├── pointing.png
└── nodding.png
```

Recommended tools: [Adobe Firefly](https://firefly.adobe.com), [Bing Image Creator](https://bing.com/images/create), [Picrew](https://picrew.me)

### Step 8 — Configure API keys (optional)

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-key-here
GEMINI_API_KEY=AIza-your-key-here
```

---

## Usage

```bash
# Basic text mode (local LLM)
python main.py

# With voice output
python main.py --voice-out

# With avatar
python main.py --avatar

# Full experience
python main.py --engine local --voice-out --avatar

# Set your name
python main.py --name "YourName"

# Use cloud engines
python main.py --engine openai --voice-out --avatar
python main.py --engine gemini --voice-out --avatar

# Voice input + output
python main.py --voice --avatar
```

### CLI Commands

While chatting, type these commands:

| Command | Action |
|---|---|
| `/reset` | Clear conversation memory |
| `/engine` | Show active engine |
| `/avatar` | Show avatar status |
| `/help` | Show all commands |
| `/quit` | Exit ili |

---

## Project Structure

```
ili/
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
│
├── core/
│   ├── tutor.py             # Teaching logic + gesture detection
│   ├── memory.py            # Persistent session memory
│   └── engine_router.py     # Engine factory
│
├── engines/
│   ├── base_engine.py       # Abstract engine interface
│   ├── local_engine.py      # Ollama (local LLM)
│   ├── openai_engine.py     # OpenAI GPT
│   └── gemini_engine.py     # Google Gemini
│
├── voice/
│   ├── text_to_speech.py    # Piper TTS
│   ├── speech_to_text.py    # whisper.cpp STT
│   └── piper/               # Piper binary + voice model
│
├── avatar/
│   ├── avatar_window.py     # Pygame avatar window
│   ├── animator.py          # Animation state machine
│   └── assets/              # Character images
│
├── ui/
│   └── cli.py               # Interactive CLI loop
│
└── memory/
    └── sessions/            # Saved conversation files (auto-created)
```

---

## Roadmap

### v1.0 — Foundation ✅
- [x] Local LLM engine (Ollama)
- [x] Cloud engines (OpenAI, Gemini)
- [x] Offline TTS (Piper)
- [x] Offline STT (whisper.cpp)
- [x] Animated avatar (pygame)
- [x] Context-based gestures
- [x] Persistent session memory

### v1.1 — Subject Modes 🔜
- [ ] Math tutor mode (step-by-step equations)
- [ ] Science tutor mode
- [ ] Language learning mode
- [ ] Coding tutor mode

### v1.2 — Web UI 🔜
- [ ] Browser-based chat interface
- [ ] Avatar in browser (via WebSocket)
- [ ] Mobile-friendly layout

### v1.3 — Advanced Features 🔜
- [ ] Student progress tracking
- [ ] Quiz generation and grading
- [ ] Multi-language support
- [ ] Plugin system for custom engines

### v2.0 — Platform 🔜
- [ ] Linux and macOS support
- [ ] Docker container
- [ ] API server mode
- [ ] Mobile app (Android/iOS)

---

## Contributing

We welcome contributions of all kinds! See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

**Quick start for contributors:**

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests (coming soon)
5. Submit a pull request

**Good first issues to tackle:**
- Add Linux/macOS support
- Add new voice models
- Improve avatar gestures
- Add new LLM engines
- Write tests
- Improve documentation

---

## FAQ

**Q: Does ili send my data anywhere?**
A: No. When using local engines, everything stays on your machine. Cloud engines (OpenAI, Gemini) send only your messages to their respective APIs — same as using ChatGPT directly.

**Q: What GPU do I need?**
A: ili works on CPU-only machines. A GPU speeds up local LLM inference. 4GB VRAM runs phi3.5 comfortably. 8GB+ runs larger models.

**Q: Can I use my own avatar images?**
A: Yes! Just place PNG images in `avatar/assets/` with the correct filenames. Any art style works.

**Q: Can I add my own LLM engine?**
A: Yes! Extend `engines/base_engine.py` and implement `generate()` and `is_available()`. Then register it in `core/engine_router.py`.

**Q: Does it work on Mac/Linux?**
A: The core Python code works everywhere. Voice binaries (Piper, whisper.cpp) need platform-specific versions. Full cross-platform support is on the roadmap.

**Q: Is it free?**
A: Completely free and open source (MIT license). Local engines cost nothing. Cloud engines use your own API keys and may incur costs.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ for learners everywhere**

⭐ Star this repo if ili helped you learn something today!

</div>
