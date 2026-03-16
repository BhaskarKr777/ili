<div align="center">

<h1>ili — Interactive Learning Intelligence</h1>

<img src="banner.png" alt="ili banner" width="60%" />

<p>
  <strong>A fully offline, open-source AI tutor for your desktop.<br>
  Voice, avatar, subject modes, persistent memory, and full computer control — no cloud, no subscriptions.</strong>
</p>

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://ollama.ai"><img src="https://img.shields.io/badge/Powered%20by-Ollama-black.svg" alt="Powered by Ollama"></a>
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
  <a href="https://github.com/BhaskarKr777/ili/releases"><img src="https://img.shields.io/badge/version-2.0-orange.svg" alt="Version 2.0"></a>
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Platform: Windows">
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

**ili** (Interactive Learning Intelligence) is a local desktop AI tutor that runs entirely on your machine — no internet required, no API subscriptions, no data leaving your computer.

It is built for students who want a personal tutor that:
- Explains any topic step by step in plain language
- Speaks responses aloud using offline text-to-speech
- Shows an animated avatar that reacts while teaching
- Remembers your study sessions across days
- Switches between subject modes (Math, Science, Coding, and more)
- Controls your computer on your behalf — volume, files, notifications, browser, and more

ili runs on consumer hardware. A GTX 1650 with 4GB VRAM is enough to run phi3.5 locally at full speed.

---

## Features

| Feature | Status |
|---|---|
| Local LLM via Ollama (fully offline) | Ready |
| Cloud engines — OpenAI GPT, Google Gemini | Ready |
| Offline voice output via Piper TTS | Ready |
| Offline voice input via faster-whisper | Ready |
| PyQt5 chat UI with avatar, history, mode switcher | Ready |
| Animated pygame avatar — drag anywhere on screen | Ready |
| Context-based gestures (thinking, talking, happy, etc.) | Ready |
| Persistent session memory — 7 day history | Ready |
| 7 subject modes | Ready |
| One-click installer via setup.py | Ready |
| Agent mode — 14 computer-control tools | New in v2.0 |
| Quiz system | Coming soon |
| Progress tracker | Coming soon |
| Flashcard mode | Coming soon |

---

## Screenshots

> Screenshots and demo GIF coming soon. Contributors welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Agent Mode

New in v2.0 — ili can control your computer through permission-gated tools. Every action requires your explicit approval before it runs.

```bash
python main.py --engine local --agent
```

Just talk naturally:

| What you say | What ili does |
|---|---|
| `"search for merge sort tutorial"` | Web search via DuckDuckGo |
| `"open a YouTube video on Newton's laws"` | Opens browser with top result |
| `"read the text on my screen"` | OCR via easyocr |
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

### All 14 Tools

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
| Code Writer | `write_code` | Generate and save code files via LLM |
| Volume | `volume` | Control system audio |
| Notes | `notes` | Persistent study notes |
| PDF Reader | `read_pdf` | Extract text from PDFs |
| YouTube | `youtube` | Search and open YouTube videos |

---

## Installation

### Requirements

- Python 3.10 or higher
- Windows 10 or 11
- 4GB RAM minimum (8GB recommended)
- GPU optional — speeds up local LLM inference

### Quick install (recommended)

```bash
git clone https://github.com/BhaskarKr777/ili.git
cd ili
python setup.py
```

The setup wizard installs all dependencies, sets up Ollama, and configures voice automatically.

### Manual install

**Step 1 — Clone and create a virtual environment**

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

**Step 2 — Set up Ollama (local LLM)**

Download and install [Ollama](https://ollama.ai), then pull a model:

```bash
ollama pull phi3.5       # 2.2GB — best for 4GB VRAM
ollama pull llama3.2     # 2GB   — faster responses
ollama pull mistral      # 4GB   — highest quality
```

Start Ollama before running ili:
```bash
ollama serve
```

**Step 3 — Voice output (optional)**

Download these files and place them in `voice/piper/`:
- [piper.exe](https://github.com/rhasspy/piper/releases/latest) — extract from `piper_windows_amd64.zip`
- [en_US-lessac-medium.onnx](https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/lessac/medium) — voice model
- `en_US-lessac-medium.onnx.json` — config file (comes with the model)

**Step 4 — Voice input (optional)**

faster-whisper downloads its model automatically on first use. Just install the dependency:

```bash
pip install faster-whisper
```

The `small` English model (~460MB) will be downloaded and cached on first voice input.

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

**Step 6 — API keys for cloud engines (optional)**

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
# Default — launches GUI with local engine
python main.py

# With agent (computer control)
python main.py --agent

# With voice output
python main.py --voice-out

# With voice input and output
python main.py --voice

# Start in a specific mode
python main.py --mode math
python main.py --mode coding

# Set your name
python main.py --name "YourName"

# Use cloud engines
python main.py --engine openai
python main.py --engine gemini

# Terminal mode (no GUI)
python main.py --cli

# Terminal mode with floating avatar
python main.py --cli --avatar

# Check system status
python setup.py --check
```

### In-app commands (terminal/CLI mode)

| Command | Action |
|---|---|
| `/mode math` | Switch to math tutor mode |
| `/modes` | List all available modes |
| `/reset` | Clear conversation memory |
| `/engine` | Show current engine and mode |
| `/tools` | List available agent tools |
| `/help` | Show all commands |
| `/quit` | Exit ili |

---

## Subject Modes

ili has 7 built-in modes. Switch anytime from the dropdown in the GUI or with `/mode <name>` in terminal:

| Mode | Command | Best for |
|---|---|---|
| General | `/mode general` | Any topic, open conversation |
| Math | `/mode math` | Algebra, calculus, geometry, equations |
| Science | `/mode science` | Physics, chemistry, biology |
| Coding | `/mode coding` | Python, JavaScript, DSA, debugging |
| Language | `/mode language` | Grammar, vocabulary, writing |
| History | `/mode history` | World history, events, civilizations |
| Friend | `/mode friend` | Casual chat, no studying required |

---

## Project Structure

```
ili/
├── main.py                   # Entry point
├── setup.py                  # Installer and system check
├── requirements.txt
├── .env.example
│
├── core/
│   ├── tutor.py              # Teaching logic and gesture detection
│   ├── memory.py             # Persistent session memory
│   ├── modes.py              # Subject mode definitions
│   ├── agent.py              # Agent — tool selection and execution
│   ├── engine_router.py      # Engine factory
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
│   ├── local_engine.py       # Ollama
│   ├── openai_engine.py
│   └── gemini_engine.py
│
├── voice/
│   ├── text_to_speech.py     # Piper TTS (offline)
│   ├── speech_to_text.py     # faster-whisper STT (offline)
│   └── piper/                # Piper binary and voice model
│
├── avatar/
│   ├── avatar_window.py      # Pygame avatar (draggable, always on top)
│   ├── animator.py
│   └── assets/               # Character PNG images
│
├── ui/
│   ├── cli.py                # Terminal UI
│   └── chat_window.py        # PyQt5 GUI
│
└── memory/
    └── sessions/             # Auto-saved conversation history
```

---

## Roadmap

### v1.0 — Foundation
- [x] Local LLM via Ollama
- [x] Cloud engines (OpenAI, Gemini)
- [x] Offline TTS via Piper
- [x] Offline STT via whisper.cpp
- [x] Animated pygame avatar (draggable)
- [x] Context-based gestures
- [x] Persistent session memory (7 days)
- [x] 7 subject modes
- [x] Cross-platform installer

### v2.0 — Agent + UI
- [x] PyQt5 chat UI with avatar, chat history, mode switcher
- [x] Document upload (PDF, txt, code files)
- [x] Voice input/output toggle in GUI
- [x] Agent system with permission-gated tool execution
- [x] Web search (DuckDuckGo + Wikipedia)
- [x] Clipboard read/write
- [x] Screen OCR via easyocr
- [x] Instant and scheduled desktop notifications
- [x] Code writer (generates, saves, opens in Notepad)
- [x] System volume control
- [x] Persistent study notes
- [x] PDF text extraction
- [x] YouTube search and open
- [x] Switched STT to faster-whisper

### v2.1 — Learning Tools
- [ ] Quiz system (auto-generated per subject)
- [ ] Progress tracker (topics covered, time spent)
- [ ] Flashcard mode with spaced repetition
- [ ] Pomodoro study timer

### v3.0 — Platform
- [ ] Full Linux and macOS support
- [ ] Packaged .exe installer for Windows
- [ ] Docker container
- [ ] Plugin system for custom tools and engines
- [ ] Multi-language support

---

## Contributing

All contributions are welcome — bug fixes, new tools, new engines, UI improvements, documentation. See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

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
- Add Linux and macOS voice binary support
- Improve avatar gesture variety
- Write unit tests for `core/memory.py`
- Add a new LLM engine (Groq, Mistral API, etc.)
- Add screenshots and a demo GIF
- Add new agent tools

---

## FAQ

**Does ili send my data anywhere?**
No. When using local engines, everything runs on your machine and nothing leaves it. Cloud engines (OpenAI, Gemini) send only your messages to their respective APIs — the same as using their products directly.

**What GPU do I need?**
None. ili runs fully on CPU. A GPU speeds up local LLM inference — 4GB VRAM is enough for phi3.5, and 8GB or more lets you run larger models like Mistral.

**Can I use my own avatar images?**
Yes. Generate any character you like and place PNG files in `avatar/assets/` using the filenames listed in the installation section.

**Can I add my own LLM engine?**
Yes. Extend `engines/base_engine.py`, implement `generate()` and `is_available()`, then register it in `core/engine_router.py`.

**Can I add my own agent tools?**
Yes. Extend `core/tools/base_tool.py`, implement `name`, `description`, and `run()`, then add it to `core/tools/__init__.py`. The agent picks it up automatically with no other changes needed.

**Does it work on Mac/Linux?**
The core Python code is cross-platform. Voice binaries currently need Windows-specific versions. Full cross-platform support is on the roadmap.

**Is it free?**
Completely free and open source under the MIT license. Local engines cost nothing to run. Cloud engines use your own API keys at your own cost.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built for learners.

[Report a bug](../../issues) • [Request a feature](../../issues) • [Contribute](CONTRIBUTING.md)

</div>
