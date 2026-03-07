<div align="center">

<h1>ili — Interactive Learning Intelligence</h1>

<img src="banner.png" alt="ili Logo" width="40%" style="opacity:0.7;" />

<p>
  <strong>An open-source, offline-first AI tutor with voice, animated avatar, subject modes, persistent memory and agentic computer control.</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://ollama.ai"><img src="https://img.shields.io/badge/Powered%20by-Ollama-black.svg" alt="Powered by Ollama"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
  <a href="https://github.com/BhaskarKr777/ili/releases/tag/v2.0"><img src="https://img.shields.io/badge/version-2.0-orange.svg" alt="Version 2.0"></a>
</p>

<p>
  <a href="#what-is-ili">What is ili?</a> •
  <a href="#features">Features</a> •
  <a href="#agent-mode">Agent Mode</a> •
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

**ili** (Interactive Learning Intelligence) is a local desktop AI tutor that runs entirely on your computer — no internet required, no subscriptions, no data sent anywhere.

It explains topics step by step, speaks responses aloud, shows an animated avatar that reacts to context, and remembers your previous study sessions. You can switch between subject modes like Math, Science, and Coding at any time. With agent mode enabled, it can also control your computer — adjusting volume, managing files, sending notifications, opening apps, and more.

---

## Features

| Feature | Status |
|---|---|
| Local LLM engine (Ollama — fully offline) | Ready |
| OpenAI GPT engine | Ready |
| Google Gemini engine | Ready |
| Offline voice output (Piper TTS) | Ready |
| Offline voice input (whisper.cpp) | Ready |
| Animated avatar (pygame, drag anywhere) | Ready |
| Context-based gestures | Ready |
| Persistent session memory (7 days) | Ready |
| Subject modes (Math, Science, Coding, Language, History, Friend) | Ready |
| One-click installer (setup.py) | Ready |
| Agent mode with 14 computer-control tools | New in v2.0 |
| Quiz system | Coming soon |
| Progress tracker | Coming soon |
| Flashcard mode | Coming soon |

---

## Agent Mode

New in v2.0 — ili can control your computer through a set of permission-gated tools. Every action requires your approval before anything runs.

```bash
python main.py --engine local --voice-out --avatar --agent
```

| What you say | What ili does |
|---|---|
| `"search for merge sort tutorial"` | Web search via DuckDuckGo |
| `"open YouTube and play a video on Newton's laws"` | Opens browser with top result |
| `"read the text on my screen"` | OCR screenshot via easyocr |
| `"copy this to my clipboard"` | Writes to system clipboard |
| `"what's in my clipboard?"` | Reads clipboard content |
| `"set volume to 50%"` | Adjusts system volume |
| `"mute / unmute"` | Toggles mute |
| `"save a note about Newton's first law"` | Saves to persistent notes file |
| `"show me all my notes"` | Lists saved notes |
| `"search my notes for physics"` | Searches notes by keyword |
| `"read this PDF: C:/path/file.pdf"` | Extracts text from PDF |
| `"write a Python file called timer.py"` | Generates and saves code, opens in Notepad |
| `"remind me at 2:30 PM to take a break"` | Scheduled desktop notification |
| `"remind me in 20 minutes to drink water"` | Timed desktop notification |
| `"take a screenshot"` | Captures and saves screenshot |
| `"open calculator"` | Launches any app or URL |
| `"run this Python code: print(2+2)"` | Executes code and shows result |

### Tools

| Tool | Name | What it does |
|---|---|---|
| Web Search | `web_search` | DuckDuckGo + Wikipedia fallback |
| File Manager | `file_tool` | Read, write, list files |
| App Launcher | `open_app` | Open apps and URLs |
| Screenshot | `screenshot` | Capture screen |
| Code Runner | `run_code` | Execute Python and shell commands |
| Mouse/Keyboard | `mouse_tool` | Automate mouse and keyboard |
| Clipboard | `clipboard` | Read and write system clipboard |
| Screen OCR | `ocr` | Read text from screen via easyocr |
| Notifications | `notification` | Instant or scheduled desktop alerts |
| Code Writer | `write_code` | Generate code files via LLM |
| Volume | `volume` | Control system audio |
| Notes | `notes` | Persistent study notes |
| PDF Reader | `read_pdf` | Extract text from PDFs |
| YouTube | `youtube` | Search and open YouTube videos |

---

## Demo

> Screenshots and demo GIF coming soon — contributors welcome!

```
Welcome back, Bhaskar!

What would you like to do today?

  [1] General      — Chat about anything
  [2] Math         — Algebra, calculus, geometry
  [3] Science      — Physics, chemistry, biology
  [4] Coding       — Python, JS, DSA, debugging
  [5] Language     — Grammar, vocabulary, writing
  [6] History      — World history, events
  [7] Friend       — Just chat, vent, chill

  Choose a mode [1-7] or press Enter for General: 2

Math mode activated. What are we solving today?

You: explain trigonometry in simple terms
ili: Trigonometry studies the relationship between angles and sides
     of triangles. Think of it like this...

You: open a YouTube video on trigonometry
ili wants to: Use tool 'youtube' with input: trigonometry explained
  Allow this? [Y/n]: y
Opening: Trigonometry For Beginners!
```

---

## Installation

### Requirements

- Python 3.10 or higher
- Windows 10/11 (macOS/Linux support in progress)
- 4GB+ RAM (8GB recommended)
- GPU optional but speeds up local LLM inference

### Quick install

```bash
git clone https://github.com/BhaskarKr777/ili.git
cd ili
python setup.py
```

The setup wizard handles dependencies, Ollama, voice, and configuration automatically.

### Manual install

**Step 1 — Clone and create environment**

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

**Step 2 — Set up local LLM**

Install [Ollama](https://ollama.ai) then pull a model:

```bash
ollama pull phi3.5       # 2.2GB — recommended for 4GB VRAM
ollama pull llama3.2     # 2GB   — faster
ollama pull mistral      # 4GB   — best quality
```

**Step 3 — Voice output (optional)**

Download and place in `voice/piper/`:
- [piper.exe](https://github.com/rhasspy/piper/releases/latest) from `piper_windows_amd64.zip`
- [en_US-lessac-medium.onnx](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium) — voice model and .json config

**Step 4 — Voice input (optional)**

Download and place in `voice/whisper/`:
- [whisper-cli.exe](https://github.com/ggerganov/whisper.cpp/releases/latest) from `whisper-bin-x64.zip`
- [ggml-small.bin](https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin) into `voice/whisper/models/`

**Step 5 — Avatar images (optional)**

Generate character images using any AI art tool and place PNG files in `avatar/assets/`:

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

Suggested tools: [Adobe Firefly](https://firefly.adobe.com), [Bing Image Creator](https://bing.com/images/create), [Picrew](https://picrew.me)

**Step 6 — API keys (optional)**

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
# Full experience
python main.py --engine local --voice-out --avatar

# With computer control
python main.py --engine local --voice-out --avatar --agent

# Text only
python main.py

# Start in a specific mode
python main.py --mode math
python main.py --mode friend

# Set your name
python main.py --name "YourName"

# Voice input and output
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
| General | `/mode general` | Any topic, mixed learning |
| Math | `/mode math` | Step-by-step equations, algebra, calculus |
| Science | `/mode science` | Physics, chemistry, biology |
| Coding | `/mode coding` | Python, JavaScript, DSA, debugging |
| Language | `/mode language` | Grammar, vocabulary, writing |
| History | `/mode history` | World history, civilizations, events |
| Friend | `/mode friend` | Just chat — no studying required |

---

## Project Structure

```
ili/
├── main.py
├── setup.py
├── requirements.txt
├── .env.example
│
├── core/
│   ├── tutor.py
│   ├── memory.py
│   ├── modes.py
│   ├── agent.py
│   ├── engine_router.py
│   └── tools/
│       ├── base_tool.py
│       ├── web_search.py
│       ├── file_tool.py
│       ├── app_tool.py
│       ├── screenshot_tool.py
│       ├── code_tool.py
│       ├── mouse_tool.py
│       ├── clipboard_tool.py
│       ├── ocr_tool.py
│       ├── notification_tool.py
│       ├── code_writer_tool.py
│       ├── volume_tool.py
│       ├── notes_tool.py
│       ├── pdf_reader_tool.py
│       └── youtube_tool.py
│
├── engines/
│   ├── base_engine.py
│   ├── local_engine.py
│   ├── openai_engine.py
│   └── gemini_engine.py
│
├── voice/
│   ├── text_to_speech.py
│   ├── speech_to_text.py
│   └── piper/
│
├── avatar/
│   ├── avatar_window.py
│   ├── animator.py
│   └── assets/
│
├── ui/
│   └── cli.py
│
└── memory/
    └── sessions/
```

---

## Roadmap

### v1.0 — Foundation
- [x] Local LLM engine (Ollama)
- [x] Cloud engines (OpenAI, Gemini)
- [x] Offline TTS (Piper)
- [x] Offline STT (whisper.cpp)
- [x] Animated avatar (pygame, draggable)
- [x] Context-based gestures
- [x] Persistent session memory (7 days)
- [x] Subject modes
- [x] Cross-platform installer

### v2.0 — Agent Tools
- [x] Agent system with permission-gated tool execution
- [x] Web search (DuckDuckGo + Wikipedia)
- [x] Clipboard read/write
- [x] Screen OCR (easyocr)
- [x] Instant and scheduled desktop notifications
- [x] Code writer (generates, saves, opens in Notepad)
- [x] System volume control
- [x] Persistent study notes
- [x] PDF text extraction
- [x] YouTube search and open

### v2.1 — Learning Tools
- [ ] Quiz system (auto-generated per subject)
- [ ] Progress tracker (topics covered, time spent)
- [ ] Flashcard mode (spaced repetition)
- [ ] Pomodoro study timer

### v3.0 — Platform
- [ ] Full Linux and macOS support
- [ ] Packaged .exe installer for Windows
- [ ] Docker container
- [ ] Plugin system for custom engines and modes
- [ ] Multi-language support

---

## Contributing

Contributions of all kinds are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

```bash
git clone https://github.com/BhaskarKr777/ili.git
cd ili
python setup.py
git checkout -b feature/your-feature
# make your changes
git push origin feature/your-feature
# open a pull request
```

Good first issues:
- Add Linux/macOS voice binary support
- Add new Ollama model presets
- Improve avatar gesture variety
- Write unit tests for `core/memory.py`
- Add a new LLM engine (Groq, Mistral API, etc.)
- Add screenshots and a demo GIF to the README
- Add new agent tools

---

## FAQ

**Does ili send my data anywhere?**
When using local engines, everything stays on your machine. Cloud engines (OpenAI, Gemini) send only your messages to their APIs — the same as using ChatGPT directly.

**What GPU do I need?**
None — ili works on CPU only. A GPU speeds up local LLM responses. 4GB VRAM handles phi3.5 fine. 8GB or more lets you run larger models like Mistral.

**Can I use my own avatar images?**
Yes. Generate any character you like and place PNG images in `avatar/assets/` using the filenames listed in the installation section.

**Can I add my own LLM engine?**
Yes. Extend `engines/base_engine.py`, implement `generate()` and `is_available()`, then register it in `core/engine_router.py`.

**Can I add my own agent tools?**
Yes. Extend `core/tools/base_tool.py`, implement `name`, `description`, and `run()`, then add it to `core/tools/__init__.py`. The agent picks it up automatically.

**Does it work on Mac/Linux?**
The core Python code works everywhere. Voice binaries need platform-specific versions — the installer handles this. Full cross-platform support is being worked on.

**Is it free?**
Completely free and open source under the MIT license. Local engines cost nothing to run. Cloud engines use your own API keys.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built for learners.

[Report a bug](../../issues) • [Request a feature](../../issues) • [Contribute](CONTRIBUTING.md)

</div>
