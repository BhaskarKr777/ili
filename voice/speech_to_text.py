import os
import sys
import subprocess
import tempfile

# ─── Paths ────────────────────────────────────────────────────────────────────
_VOICE_DIR   = os.path.dirname(os.path.abspath(__file__))
_WHISPER_DIR = os.path.join(_VOICE_DIR, "whisper")
_WHISPER_CLI = os.path.join(_WHISPER_DIR, "whisper-cli.exe")
_MODEL_PATH  = os.path.join(_WHISPER_DIR, "models", "ggml-small.bin")

# ─── Settings ─────────────────────────────────────────────────────────────────
SAMPLE_RATE    = 16000
CHANNELS       = 1
RECORD_SECONDS = 6


def _check_setup() -> bool:
    ok = True
    if not os.path.isfile(_WHISPER_CLI):
        print(f"[STT] ⚠ whisper-cli.exe not found at: {_WHISPER_CLI}")
        ok = False
    if not os.path.isfile(_MODEL_PATH):
        print(f"[STT] ⚠ Model not found at: {_MODEL_PATH}")
        ok = False
    return ok


def record_audio() -> str | None:
    """Record from mic, save to temp WAV, return file path."""
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        print("[STT] ⚠ Run: pip install sounddevice soundfile")
        return None

    print(f"🎙  Listening for {RECORD_SECONDS} seconds... speak now!")

    try:
        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
        )
        sd.wait()
    except Exception as e:
        print(f"[STT] ⚠ Recording failed: {e}")
        return None

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, SAMPLE_RATE)
    return tmp.name


def transcribe(wav_path: str) -> str:
    """Run whisper-cli.exe on WAV file, return transcribed text."""
    if not _check_setup():
        return ""

    try:
        result = subprocess.run(
            [
                _WHISPER_CLI,
                "-m", _MODEL_PATH,
                "-f", wav_path,
                "--no-timestamps",
                "-l", "en",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

         # Debug — show exactly what whisper returned
        print(f"[STT DEBUG] returncode: {result.returncode}")
        print(f"[STT DEBUG] stdout: '{result.stdout.strip()}'")
        print(f"[STT DEBUG] stderr: '{result.stderr.strip()[:300]}'")

        text = result.stdout.strip()

        # Remove any leftover timestamp lines just in case
        lines = [
            line.strip() for line in text.splitlines()
            if line.strip() and "-->" not in line and not line.startswith("[")
        ]
        return " ".join(lines).strip()

    except subprocess.TimeoutExpired:
        print("[STT] ⚠ Whisper timed out.")
        return ""
    except Exception as e:
        print(f"[STT] ⚠ Transcription failed: {e}")
        return ""
    finally:
        try:
            os.unlink(wav_path)
        except Exception:
            pass


def listen() -> str:
    """Full pipeline: record → transcribe → return text."""
    wav_path = record_audio()
    if not wav_path:
        return ""

    print("🔍 Transcribing...")
    text = transcribe(wav_path)

    if text:
        print(f"📝 You said: {text}")
    else:
        print("[STT] Could not transcribe. Please try again.")

    return text