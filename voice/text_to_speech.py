import os
import subprocess
import tempfile
import threading
from typing import Callable

# ─── Paths ────────────────────────────────────────────────────────────────────
_VOICE_DIR   = os.path.dirname(os.path.abspath(__file__))
_PIPER_DIR   = os.path.join(_VOICE_DIR, "piper")
_PIPER_EXE   = os.path.join(_PIPER_DIR, "piper.exe")
_VOICE_MODEL = os.path.join(_PIPER_DIR, "en_US-lessac-medium.onnx")
_VOICE_JSON  = os.path.join(_PIPER_DIR, "en_US-lessac-medium.onnx.json")


def _check_setup() -> bool:
    ok = True
    for path, label in [
        (_PIPER_EXE,   "piper.exe"),
        (_VOICE_MODEL, "en_US-lessac-medium.onnx"),
        (_VOICE_JSON,  "en_US-lessac-medium.onnx.json"),
    ]:
        if not os.path.isfile(path):
            print(f"[TTS] ⚠ {label} not found at: {path}")
            ok = False
    return ok


def _play_wav(wav_path: str):
    """
    Play a WAV file.
    Tries sounddevice first, falls back to pygame if it fails.
    """
    # ── Try sounddevice ───────────────────────────────────────────────
    try:
        import sounddevice as sd
        import soundfile as sf
        data, samplerate = sf.read(wav_path, dtype="float32")
        sd.play(data, samplerate)
        sd.wait()
        return
    except Exception as e:
        print(f"[TTS] sounddevice failed ({e}), trying pygame...")

    # ── Fallback: pygame mixer ─────────────────────────────────────────
    try:
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.music.load(wav_path)
        pygame.mixer.music.play()
        import time
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        return
    except Exception as e:
        print(f"[TTS] pygame fallback also failed: {e}")


def speak(
    text: str,
    on_start: Callable = None,
    on_stop: Callable = None,
    blocking: bool = True,
) -> None:
    """
    Convert text to speech using Piper and play it.

    Args:
        text:      The text to speak
        on_start:  Callback fired when audio starts (used by avatar)
        on_stop:   Callback fired when audio finishes (used by avatar)
        blocking:  If True, waits for playback to finish before returning
    """
    if not _check_setup():
        print("[TTS] Skipping speech — setup incomplete.")
        return

    # Skip empty or whitespace-only text
    if not text or not text.strip():
        print("[TTS] Skipping speech — empty text.")
        return

    def _run():
        tmp_wav_path = None
        tmp_txt_path = None

        try:
            # ── Write text to temp file ───────────────────────────────
            tmp_wav = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            tmp_wav_path = tmp_wav.name
            tmp_wav.close()

            tmp_txt = tempfile.NamedTemporaryFile(
                suffix=".txt", delete=False, mode="w", encoding="utf-8"
            )
            tmp_txt.write(text.strip())
            tmp_txt.close()
            tmp_txt_path = tmp_txt.name

            # ── Run Piper ─────────────────────────────────────────────
            with open(tmp_txt_path, "r", encoding="utf-8") as f:
                proc = subprocess.run(
                    [
                        _PIPER_EXE,
                        "--model",       _VOICE_MODEL,
                        "--config",      _VOICE_JSON,
                        "--output_file", tmp_wav_path,
                    ],
                    stdin=f,
                    capture_output=True,
                    timeout=30,
                )

            if proc.returncode != 0:
                print(f"[TTS] ⚠ Piper error: {proc.stderr.decode(errors='ignore').strip()}")
                return

            if not os.path.isfile(tmp_wav_path) or os.path.getsize(tmp_wav_path) == 0:
                print("[TTS] ⚠ WAV file was not created or is empty.")
                return

            # ── Fire avatar start callback ─────────────────────────────
            if on_start:
                on_start()

            # ── Play audio ────────────────────────────────────────────
            _play_wav(tmp_wav_path)

            # ── Fire avatar stop callback ──────────────────────────────
            if on_stop:
                on_stop()

        except subprocess.TimeoutExpired:
            print("[TTS] ⚠ Piper timed out.")
        except Exception as e:
            print(f"[TTS] ⚠ Unexpected error: {e}")
        finally:
            # Clean up temp files
            for path in [tmp_wav_path, tmp_txt_path]:
                if path:
                    try:
                        os.unlink(path)
                    except Exception:
                        pass

    if blocking:
        _run()
    else:
        threading.Thread(target=_run, daemon=True).start()