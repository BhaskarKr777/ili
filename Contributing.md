# Contributing to ili

First off — thank you for taking the time to contribute! 🎉

ili is an open source project and we welcome contributions of all kinds: bug fixes, new features, documentation improvements, new LLM engines, avatar improvements, and more.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Submitting a Pull Request](#submitting-a-pull-request)
- [Good First Issues](#good-first-issues)
- [Style Guide](#style-guide)

---

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). In short: be kind, be respectful, be constructive.

---

## How to Contribute

### Reporting Bugs

1. Check if the bug is already reported in [Issues](../../issues)
2. If not, open a new issue with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your OS, Python version, GPU

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe what you want and why it would help learners
3. We'll discuss and add it to the roadmap if it fits

### Contributing Code

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ili.git
cd ili

# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run ili
python main.py
```

---

## Adding a New LLM Engine

This is one of the best ways to contribute! Here's how:

1. Create `engines/your_engine.py`:

```python
from engines.base_engine import BaseEngine

class YourEngine(BaseEngine):
    def __init__(self):
        pass

    def generate(self, prompt: str) -> str:
        # Your implementation here
        return "response"

    def is_available(self) -> bool:
        # Check if engine is ready
        return True
```

2. Register it in `core/engine_router.py`:

```python
SUPPORTED_ENGINES = ["local", "openai", "gemini", "your_engine"]

def get_engine(name: str) -> BaseEngine:
    ...
    elif name == "your_engine":
        from engines.your_engine import YourEngine
        return YourEngine()
```

3. Document it in `README.md`

---

## Submitting a Pull Request

1. Make sure your code runs without errors
2. Keep PRs focused — one feature or fix per PR
3. Write a clear PR description explaining what you changed and why
4. Reference any related issues (e.g. `Fixes #42`)

**PR title format:**
```
feat: add groq engine support
fix: avatar gesture not switching correctly
docs: update installation guide for macOS
chore: update dependencies
```

---

## Good First Issues

New to the project? These are great starting points:

- 🐛 Fix voice input on Linux/macOS
- 📝 Improve README with screenshots
- 🌍 Add support for non-English Piper voice models
- 🧪 Write basic unit tests for `core/memory.py`
- 🎨 Improve avatar fallback when images are missing
- ⚙️ Add a `--list-models` flag to show available Ollama models
- 🔌 Add Groq engine (fast free cloud inference)
- 🔌 Add Mistral API engine

---

## Style Guide

- Use Python type hints where possible
- Keep functions small and focused
- Comment non-obvious code
- Use descriptive variable names
- Follow existing code style in each file

---

Thank you again for contributing to ili! Every contribution — big or small — helps make AI tutoring accessible to more learners around the world. 🌍
