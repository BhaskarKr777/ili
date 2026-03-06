<div align="center">

<h1>ili — Interactive Learning Intelligence</h1>

<img src="banner.png" alt="ili Logo" width="40%" style="opacity:0.7;" />

<p>
  <strong>
    An open-source, offline-first AI tutor with voice, animated avatar, subject modes and persistent memory.
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
  <a href="#what-is-ili">What is ili?</a> •
  <a href="#features">Features</a> •
  <a href="#installation">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#subject-modes">Modes</a> •
  <a href="#roadmap">Roadmap</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#faq">FAQ</a>
</p>

</div>

---

## What is ili?

**ili** (Interactive Learning Intelligence) is a **local desktop AI tutor** that runs entirely on your computer — no internet required, no subscriptions, no data sent anywhere.

Think of ili as a personal tutor and friend who:
- Explains any topic clearly, step by step
- Speaks responses aloud with a natural voice
- Shows an animated avatar that reacts to context
- Remembers your previous study sessions
- Switches between subject modes (Math, Science, Coding, and more)
- Can just chat when you need a break from studying

---

## Features

| Feature | Status |
|---|---|
| 🧠 Local LLM engine (Ollama — fully offline) | ✅ Ready |
| ☁️ OpenAI GPT engine | ✅ Ready |
| ☁️ Google Gemini engine | ✅ Ready |
| 🔊 Offline voice output (Piper TTS) | ✅ Ready |
| 🎙️ Offline voice input (whisper.cpp) | ✅ Ready |
| 🧑‍🎨 Animated avatar (pygame, drag anywhere) | ✅ Ready |
| 🖐️ Context-based gestures | ✅ Ready |
| 💾 Persistent session memory (7 days) | ✅ Ready |
| 📚 Subject modes (Math, Science, Coding, Language, History, Friend) | ✅ Ready |
| ⚙️ One-click installer (setup.py) | ✅ Ready |
| 📝 Quiz system | 🔜 Coming soon |
| 📊 Progress tracker | 🔜 Coming soon |
| 🃏 Flashcard mode | 🔜 Coming soon |
| 🌍 Multi-language support | 🔜 Coming soon |

---

## Demo

> 📸 _Screenshots and demo GIF coming soon — contributors welcome!_

```
👋 Welcome back, Bhaskar!

🎓 What would you like to do today?

  [1] 🌟  General      — Chat about anything
  [2] 🔢  Math         — Algebra, calculus, geometry
  [3] 🔬  Science      — Physics, chemistry, biology
  [4] 💻  Coding       — Python, JS, DSA, debugging
  [5] 📝  Language     — Grammar, vocabulary, writing
  [6] 🏛️  History      — World history, events
  [7] 💬  Friend       — Just chat, vent, chill

  Choose a mode [1-7] or press Enter for General: 2

🔢 Math mode activated! What are we solving today?

You: explain trigonometry in simple terms
🔢 ili: Trigonometry studies the relationship between angles and sides
       of triangles. Think of it like this...
       [avatar switches to pointing gesture, speaks response aloud]
```

---

## Installation

### Requirements

- Python 3.10 or higher
- Windows 10/11 (macOS/Linux support in progress)
- 4GB+ RAM (8GB recommended)
- GPU optional but speeds up local LLM

### Quick install (recommended)

```bash
git clone https://github.com/BhaskarKr777/ili.git
cd ili
python setup.py
```

The setup wizard will guide you through everything — dependencies, Ollama, voice, and more.

### Manual install

#### Step 1 — Clone and set up environment

```bash
git clone https://github.com/BhaskarKr777/ili.git
cd ili
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Step 2 — Set up local LLM

Install [Ollama](https://ollama.ai) then pull a model:

```bash
ollama pull phi3.5       # 2.2GB — recommended for 4GB VRAM
ollama pull llama3.2     # 2GB   — faster responses
ollama pull mistral      # 4GB   — best quality
```

#### Step 3 — Voice output (optional)

Download and place in `voice/piper/`:
- [piper.exe](https://github.com/rhasspy/piper/releases/latest) — from `piper_windows_amd64.zip`
- [en_US-lessac-medium.onnx](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium) — voice model + .json config

#### Step 4 — Voice input (optional)

Download and place in `voice/whisper/`:
- [whisper-cli.exe](https://github.com/ggerganov/whisper.cpp/releases/latest) — from `whisper-bin-x64.zip`
- [ggml-small.bin](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin) → `voice/whisper/models/`

#### Step 5 — Avatar images (optional)

Generate character images using any AI art tool and place in `avatar/assets/`:

```
avatar/assets/
├── idle.png           ← neutral expression
├── idle_breathe.png   ← subtle variation
├── talking_1.png      ← speaking, one hand gesturing
├── talking_2.png      ← speaking, both hands gesturing
├── thinking.png       ← finger on chin, eyes up
├── happy.png          ← excited, big smile
├── confused.png       ← tilted head, raised eyebrow
├── pointing.png       ← pointing forward
└── nodding.png        ← agreeing, soft smile
```

Recommended tools: [Adobe Firefly](https://firefly.adobe.com), [Bing Image Creator](https://bing.com/images/create), [Picrew](https://picrew.me)

#### Step 6 — API keys (optional)

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
# Full experience (recommended)
python main.py --engine local --voice-out --avatar

# Text only
python main.py

# Start in a specific mode
python main.py --mode math
python main.py --mode friend

# Set your name
python main.py --name "YourName"

# Voice input + output
python main.py --voice --avatar

# Cloud engines
python main.py --engine openai --voice-out --avatar
python main.py --engine gemini --voice-out --avatar

# Check system status
python setup.py --check
```

### CLI Commands

| Command | Action |
|---|---|
| `/mode math` | Switch to math tutor mode |
| `/modes` | List all available modes |
| `/reset` | Clear conversation memory |
| `/engine` | Show active engine and mode |
| `/help` | Show all commands |
| `/quit` | Exit ili |

---

## Subject Modes

ili has 7 modes — switch anytime with `/mode <name>`:

| Mode | Command | Best for |
|---|---|---|
| 🌟 General | `/mode general` | Any topic, mixed learning |
| 🔢 Math | `/mode math` | Step-by-step equations, algebra, calculus |
| 🔬 Science | `/mode science` | Physics, chemistry, biology |
| 💻 Coding | `/mode coding` | Python, JavaScript, DSA, debugging |
| 📝 Language | `/mode language` | Grammar, vocabulary, writing |
| 🏛️ History | `/mode history` | World history, civilizations, events |
| 💬 Friend | `/mode friend` | Just chat — no studying required |

---

## Project Structure

```
ili/
├── main.py                  # Entry point
├── setup.py                 # Installer and system check
├── requirements.txt         # Python dependencies
├── .env.example             # API key template
│
├── core/
│   ├── tutor.py             # Teaching logic + gesture detection
│   ├── memory.py            # Persistent session memory
│   ├── modes.py             # Subject mode definitions
│   └── engine_router.py     # Engine factory
│
├── engines/
│   ├── base_engine.py       # Abstract engine interface
│   ├── local_engine.py      # Ollama (offline LLM)
│   ├── openai_engine.py     # OpenAI GPT
│   └── gemini_engine.py     # Google Gemini
│
├── voice/
│   ├── text_to_speech.py    # Piper TTS (offline)
│   ├── speech_to_text.py    # whisper.cpp STT (offline)
│   └── piper/               # Piper binary + voice model
│
├── avatar/
│   ├── avatar_window.py     # Pygame avatar (draggable)
│   ├── animator.py          # Animation state machine
│   └── assets/              # Your character images
│
├── ui/
│   └── cli.py               # Interactive terminal UI
│
└── memory/
    └── sessions/            # Auto-saved conversation history
```

---

## Roadmap

### v1.0 — Foundation ✅
- [x] Local LLM engine (Ollama)
- [x] Cloud engines (OpenAI, Gemini)
- [x] Offline TTS (Piper)
- [x] Offline STT (whisper.cpp)
- [x] Animated avatar (pygame, draggable)
- [x] Context-based gestures
- [x] Persistent session memory (7 days)
- [x] Subject modes (Math, Science, Coding, Language, History, Friend)
- [x] Cross-platform installer (setup.py)

### v1.1 — Learning Tools 🔜
- [ ] Quiz system (auto-generated per subject)
- [ ] Progress tracker (topics covered, time spent)
- [ ] Flashcard mode (spaced repetition)
- [ ] Notes system (save key points per session)

### v1.2 — Accessibility 🔜
- [ ] Multi-language support (Hindi, Spanish, French, etc.)
- [ ] Voice input fix and improvements
- [ ] Pomodoro study timer
- [ ] Font size and theme settings

### v2.0 — Platform 🔜
- [ ] Full Linux and macOS support
- [ ] Packaged .exe installer for Windows
- [ ] Docker container
- [ ] Plugin system for custom engines and modes

---

## Contributing

We welcome contributions of all kinds! See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

**Quick start:**

```bash
git clone https://github.com/BhaskarKr777/ili.git
cd ili
python setup.py
git checkout -b feature/your-feature
# make changes
git push origin feature/your-feature
# open a pull request
```

**Good first issues:**
- Add Linux/macOS voice binary support
- Add new Ollama model presets
- Improve avatar gesture variety
- Write unit tests for `core/memory.py`
- Add a new LLM engine (Groq, Mistral API, etc.)
- Improve README with screenshots

---

## FAQ

**Q: Does ili send my data anywhere?**
A: No. When using local engines, everything stays on your machine. Cloud engines (OpenAI, Gemini) send only your messages to their APIs — same as using ChatGPT directly.

**Q: What GPU do I need?**
A: None — ili works on CPU only. A GPU speeds up local LLM responses. 4GB VRAM runs phi3.5 comfortably. 8GB+ runs larger models like Mistral.

**Q: Can I use my own avatar images?**
A: Yes! Generate any character you like and place PNG images in `avatar/assets/` with the correct filenames.

**Q: Can I add my own LLM engine?**
A: Yes! Extend `engines/base_engine.py`, implement `generate()` and `is_available()`, then register it in `core/engine_router.py`.

**Q: Does it work on Mac/Linux?**
A: The core Python code works everywhere. Voice binaries need platform-specific versions — the installer handles this automatically. Full cross-platform support is actively being worked on.

**Q: Is it free?**
A: Completely free and open source (MIT license). Local engines cost nothing to run. Cloud engines use your own API keys.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Made with ❤️ for learners everywhere**

⭐ Star this repo if ili helped you learn something today!

[Report a bug](../../issues) • [Request a feature](../../issues) • [Contribute](CONTRIBUTING.md)

</div>
