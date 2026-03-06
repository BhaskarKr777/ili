"""
ili — Interactive Learning Intelligence
========================================
Cross-platform installer and setup script.

Usage:
    python setup.py          # full interactive setup
    python setup.py --check  # check what's installed
    python setup.py --deps   # install Python dependencies only
    python setup.py --ollama # set up Ollama and models only
    python setup.py --voice  # set up voice (Piper TTS + Whisper)
"""

import os
import sys
import platform
import subprocess
import argparse
import shutil
import urllib.request
import zipfile
import json
from pathlib import Path

# ─── Detect OS ────────────────────────────────────────────────────────────────
OS        = platform.system()   # "Windows", "Darwin", "Linux"
IS_WIN    = OS == "Windows"
IS_MAC    = OS == "Darwin"
IS_LINUX  = OS == "Linux"

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.resolve()
VENV_DIR    = ROOT / "venv"
VOICE_DIR   = ROOT / "voice"
PIPER_DIR   = VOICE_DIR / "piper"
WHISPER_DIR = VOICE_DIR / "whisper"
MODELS_DIR  = WHISPER_DIR / "models"
ASSETS_DIR  = ROOT / "avatar" / "assets"
MEMORY_DIR  = ROOT / "memory" / "sessions"
ENV_FILE    = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"

# ─── Colors ───────────────────────────────────────────────────────────────────
def c(text, color):
    if IS_WIN and not _supports_color():
        return text
    colors = {
        "green":  "\033[92m",
        "yellow": "\033[93m",
        "red":    "\033[91m",
        "blue":   "\033[94m",
        "cyan":   "\033[96m",
        "bold":   "\033[1m",
        "reset":  "\033[0m",
    }
    return f"{colors.get(color, '')}{text}{colors['reset']}"

def _supports_color():
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        return True
    except Exception:
        return False

def ok(msg):   print(f"  {c('✓', 'green')}  {msg}")
def warn(msg): print(f"  {c('⚠', 'yellow')}  {msg}")
def err(msg):  print(f"  {c('✗', 'red')}  {msg}")
def info(msg): print(f"  {c('→', 'cyan')}  {msg}")
def head(msg): print(f"\n{c(msg, 'bold')}")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd, check=True, capture=False):
    """Run a shell command."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=check,
            capture_output=capture, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        return e

def pip(package):
    """Install a pip package."""
    python = _get_python()
    return run(f'"{python}" -m pip install {package} --quiet')

def _get_python():
    """Get path to Python in venv if it exists."""
    if IS_WIN:
        venv_python = VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_python = VENV_DIR / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable

def download(url, dest, label=""):
    """Download a file with progress."""
    label = label or Path(dest).name
    info(f"Downloading {label}...")
    try:
        def progress(count, block, total):
            if total > 0:
                pct = min(count * block * 100 // total, 100)
                print(f"\r    {pct}% ", end="", flush=True)
        urllib.request.urlretrieve(url, dest, progress)
        print()
        ok(f"Downloaded {label}")
        return True
    except Exception as e:
        err(f"Failed to download {label}: {e}")
        return False

def ask(prompt, default="y") -> bool:
    """Yes/no prompt."""
    yn = "Y/n" if default == "y" else "y/N"
    try:
        ans = input(f"  {prompt} [{yn}]: ").strip().lower()
        if not ans:
            return default == "y"
        return ans in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return default == "y"


# ─── Check functions ──────────────────────────────────────────────────────────

def check_python():
    head("Checking Python...")
    version = sys.version_info
    if version >= (3, 10):
        ok(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        err(f"Python {version.major}.{version.minor} found — ili requires Python 3.10+")
        info("Download Python from: https://python.org/downloads")
        return False

def check_pip():
    result = run("pip --version", check=False, capture=True)
    if result.returncode == 0:
        ok("pip is available")
        return True
    err("pip not found")
    return False

def check_ollama():
    result = run("ollama --version", check=False, capture=True)
    if result.returncode == 0:
        ok(f"Ollama installed: {result.stdout.strip()}")
        return True
    warn("Ollama not found")
    return False

def check_model(model="phi3.5"):
    result = run("ollama list", check=False, capture=True)
    if result.returncode == 0 and model in result.stdout:
        ok(f"Model '{model}' is available")
        return True
    warn(f"Model '{model}' not found")
    return False

def check_piper():
    exe = PIPER_DIR / ("piper.exe" if IS_WIN else "piper")
    if exe.exists():
        ok("Piper TTS binary found")
        return True
    warn("Piper TTS not found")
    return False

def check_whisper():
    exe = WHISPER_DIR / ("whisper-cli.exe" if IS_WIN else "whisper-cli")
    if exe.exists():
        ok("Whisper STT binary found")
        return True
    warn("Whisper STT not found")
    return False

def check_voice_model():
    model = PIPER_DIR / "en_US-lessac-medium.onnx"
    if model.exists():
        ok("Piper voice model found")
        return True
    warn("Piper voice model not found")
    return False

def check_whisper_model():
    model = MODELS_DIR / "ggml-small.bin"
    if model.exists():
        ok("Whisper model found")
        return True
    warn("Whisper model not found")
    return False

def check_env():
    if ENV_FILE.exists():
        ok(".env file exists")
        return True
    warn(".env file not found")
    return False

def check_avatar_assets():
    if ASSETS_DIR.exists():
        pngs = list(ASSETS_DIR.glob("*.png"))
        if pngs:
            ok(f"Avatar assets found ({len(pngs)} images)")
            return True
    warn("No avatar images found in avatar/assets/")
    return False

def check_deps():
    head("Checking Python dependencies...")
    required = ["pygame", "requests", "sounddevice", "soundfile", "numpy"]
    all_ok = True
    for pkg in required:
        result = run(f'"{_get_python()}" -c "import {pkg}"',
                     check=False, capture=True)
        if result.returncode == 0:
            ok(pkg)
        else:
            warn(f"{pkg} not installed")
            all_ok = False
    return all_ok


# ─── Setup steps ──────────────────────────────────────────────────────────────

def setup_venv():
    head("Setting up virtual environment...")
    if VENV_DIR.exists():
        ok("Virtual environment already exists")
        return True
    info("Creating virtual environment...")
    result = run(f'"{sys.executable}" -m venv "{VENV_DIR}"')
    if result.returncode == 0:
        ok("Virtual environment created")
        return True
    err("Failed to create virtual environment")
    return False

def setup_deps():
    head("Installing Python dependencies...")
    req_file = ROOT / "requirements.txt"
    if req_file.exists():
        python = _get_python()
        info("Installing from requirements.txt...")
        result = run(f'"{python}" -m pip install -r "{req_file}" --quiet')
        if result.returncode == 0:
            ok("All dependencies installed")
            return True
        else:
            err("Some dependencies failed to install")
            return False
    else:
        # Install manually
        packages = [
            "pygame>=2.6.0",
            "requests>=2.31.0",
            "python-dotenv>=1.0.0",
            "sounddevice>=0.4.6",
            "soundfile>=0.12.1",
            "numpy>=1.24.0",
            "openai>=1.0.0",
            "google-genai>=0.1.0",
        ]
        for pkg in packages:
            info(f"Installing {pkg}...")
            pip(pkg)
        ok("Dependencies installed")
        return True

def setup_ollama():
    head("Setting up Ollama (local LLM)...")

    if not check_ollama():
        info("Ollama needs to be installed manually.")
        if IS_WIN:
            info("Download from: https://ollama.ai/download/windows")
        elif IS_MAC:
            info("Download from: https://ollama.ai/download/mac")
        else:
            info("Install with: curl -fsSL https://ollama.ai/install.sh | sh")

        if not ask("Have you installed Ollama?", default="n"):
            warn("Skipping Ollama setup — install it manually later")
            return False

    # Pull recommended model
    info("Pulling phi3.5 model (2.2GB — this may take a few minutes)...")
    if ask("Download phi3.5 model?"):
        result = run("ollama pull phi3.5")
        if result.returncode == 0:
            ok("phi3.5 model ready")
        else:
            warn("Could not pull phi3.5 — make sure Ollama is running")
    return True

def setup_voice_output():
    head("Setting up voice output (Piper TTS)...")

    PIPER_DIR.mkdir(parents=True, exist_ok=True)

    # Platform-specific download URLs
    if IS_WIN:
        piper_url = "https://github.com/rhasspy/piper/releases/latest/download/piper_windows_amd64.zip"
        piper_zip = PIPER_DIR / "piper.zip"
    elif IS_MAC:
        piper_url = "https://github.com/rhasspy/piper/releases/latest/download/piper_macos_x64.tar.gz"
        piper_zip = PIPER_DIR / "piper.tar.gz"
    else:
        piper_url = "https://github.com/rhasspy/piper/releases/latest/download/piper_linux_x86_64.tar.gz"
        piper_zip = PIPER_DIR / "piper.tar.gz"

    if not check_piper():
        if ask("Download Piper TTS?"):
            if download(piper_url, piper_zip, "Piper TTS"):
                info("Extracting Piper...")
                try:
                    if IS_WIN:
                        with zipfile.ZipFile(piper_zip, "r") as z:
                            z.extractall(PIPER_DIR)
                    else:
                        import tarfile
                        with tarfile.open(piper_zip) as t:
                            t.extractall(PIPER_DIR)
                    piper_zip.unlink()
                    ok("Piper extracted")
                except Exception as e:
                    err(f"Extraction failed: {e}")

    if not check_voice_model():
        if ask("Download English voice model (en_US-lessac-medium, ~65MB)?"):
            model_url  = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
            config_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
            download(model_url,  PIPER_DIR / "en_US-lessac-medium.onnx",      "Voice model")
            download(config_url, PIPER_DIR / "en_US-lessac-medium.onnx.json", "Voice config")

def setup_voice_input():
    head("Setting up voice input (Whisper STT)...")

    WHISPER_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    if IS_WIN:
        whisper_url = "https://github.com/ggerganov/whisper.cpp/releases/latest/download/whisper-bin-x64.zip"
        whisper_zip = WHISPER_DIR / "whisper.zip"
    elif IS_MAC:
        whisper_url = "https://github.com/ggerganov/whisper.cpp/releases/latest/download/whisper-macos-x64.zip"
        whisper_zip = WHISPER_DIR / "whisper.zip"
    else:
        whisper_url = "https://github.com/ggerganov/whisper.cpp/releases/latest/download/whisper-linux-x64.zip"
        whisper_zip = WHISPER_DIR / "whisper.zip"

    if not check_whisper():
        if ask("Download Whisper STT?"):
            if download(whisper_url, whisper_zip, "Whisper STT"):
                info("Extracting Whisper...")
                try:
                    with zipfile.ZipFile(whisper_zip, "r") as z:
                        z.extractall(WHISPER_DIR)
                    whisper_zip.unlink()
                    ok("Whisper extracted")
                except Exception as e:
                    err(f"Extraction failed: {e}")

    if not check_whisper_model():
        if ask("Download Whisper small model (~466MB)?"):
            model_url = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin"
            download(model_url, MODELS_DIR / "ggml-small.bin", "Whisper model")

def setup_env():
    head("Setting up environment file...")
    if ENV_FILE.exists():
        ok(".env already exists")
        return

    if ENV_EXAMPLE.exists():
        shutil.copy(ENV_EXAMPLE, ENV_FILE)
        ok(".env created from .env.example")
    else:
        ENV_FILE.write_text(
            "# ili environment variables\n"
            "OPENAI_API_KEY=\n"
            "GEMINI_API_KEY=\n"
        )
        ok(".env created")

    info("Edit .env to add your OpenAI or Gemini API keys (optional)")

def setup_directories():
    """Create required directories."""
    for d in [MEMORY_DIR, ASSETS_DIR, PIPER_DIR, WHISPER_DIR, MODELS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    ok("Directory structure ready")


# ─── Full check report ────────────────────────────────────────────────────────

def run_check():
    print(c("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "cyan"))
    print(c("  ili — System Check", "bold"))
    print(c("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", "cyan"))
    print(f"  Platform: {OS} ({platform.machine()})")
    print(f"  Python:   {sys.version.split()[0]}")
    print()

    results = {
        "Python 3.10+":      check_python(),
        "Dependencies":      check_deps(),
        "Ollama":            check_ollama(),
        "phi3.5 model":      check_model("phi3.5"),
        "Piper TTS":         check_piper(),
        "Voice model":       check_voice_model(),
        "Whisper STT":       check_whisper(),
        "Whisper model":     check_whisper_model(),
        ".env file":         check_env(),
        "Avatar assets":     check_avatar_assets(),
    }

    ready = sum(results.values())
    total = len(results)

    print(c(f"\n  {ready}/{total} components ready", "bold"))

    if ready == total:
        print(c("  ili is fully set up! Run: python main.py --avatar --voice-out", "green"))
    else:
        missing = [k for k, v in results.items() if not v]
        warn(f"Missing: {', '.join(missing)}")
        info("Run: python setup.py   to fix missing components")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ili setup and installer")
    parser.add_argument("--check",  action="store_true", help="Check system status")
    parser.add_argument("--deps",   action="store_true", help="Install dependencies only")
    parser.add_argument("--ollama", action="store_true", help="Set up Ollama only")
    parser.add_argument("--voice",  action="store_true", help="Set up voice only")
    args = parser.parse_args()

    if args.check:
        run_check()
        return

    if args.deps:
        setup_deps()
        return

    if args.ollama:
        setup_ollama()
        return

    if args.voice:
        setup_voice_output()
        setup_voice_input()
        return

    # ── Full interactive setup ────────────────────────────────────────────
    print(c("""
╔══════════════════════════════════════════════╗
║     ili — Interactive Learning Intelligence  ║
║              Setup & Installer               ║
╚══════════════════════════════════════════════╝
""", "cyan"))

    print(f"  Platform : {OS}")
    print(f"  Python   : {sys.version.split()[0]}")
    print(f"  Location : {ROOT}\n")

    if not check_python():
        sys.exit(1)

    # Step 1 — Directories
    head("Step 1 — Creating directories...")
    setup_directories()

    # Step 2 — Venv
    head("Step 2 — Virtual environment...")
    if ask("Create virtual environment?"):
        setup_venv()

    # Step 3 — Dependencies
    head("Step 3 — Python dependencies...")
    if ask("Install Python dependencies?"):
        setup_deps()

    # Step 4 — Ollama
    head("Step 4 — Local LLM (Ollama)...")
    if ask("Set up Ollama for offline AI?"):
        setup_ollama()

    # Step 5 — Voice output
    head("Step 5 — Voice output (Piper TTS)...")
    if ask("Set up voice output?"):
        setup_voice_output()

    # Step 6 — Voice input
    head("Step 6 — Voice input (Whisper STT)...")
    if ask("Set up voice input (microphone)?"):
        setup_voice_input()

    # Step 7 — .env
    head("Step 7 — Environment file...")
    setup_env()

    # Step 8 — Avatar
    head("Step 8 — Avatar images...")
    if not check_avatar_assets():
        info("Generate avatar images using AI tools and place them in:")
        info(f"  {ASSETS_DIR}")
        info("Filenames: idle.png, talking_1.png, talking_2.png, thinking.png,")
        info("           happy.png, confused.png, pointing.png, nodding.png")

    # ── Done ─────────────────────────────────────────────────────────────
    print(c("""
╔══════════════════════════════════════════════╗
║          Setup complete! 🎓                  ║
╚══════════════════════════════════════════════╝
""", "green"))

    print("  Run ili:")
    print(c("    python main.py                          # text mode", "cyan"))
    print(c("    python main.py --voice-out              # with voice", "cyan"))
    print(c("    python main.py --voice-out --avatar     # full experience", "cyan"))
    print()
    print("  Check status anytime:")
    print(c("    python setup.py --check", "cyan"))
    print()


if __name__ == "__main__":
    main()