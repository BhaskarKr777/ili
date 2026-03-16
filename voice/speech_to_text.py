"""
Speech to Text — faster-whisper
================================
Fully offline, no external binaries needed.
Uses faster-whisper which runs directly in Python on CPU or GPU.

Install:
    pip install faster-whisper sounddevice soundfile
"""

import os
import tempfile

# ─── Settings ─────────────────────────────────────────────────────────────────
SAMPLE_RATE    = 16000
CHANNELS       = 1
RECORD_SECONDS = 6
WHISPER_MODEL  = "small"       # tiny, base, small, medium, large
DEVICE         = "cuda"        # "cuda" for GPU, "cpu" for CPU only
COMPUTE_TYPE   = "float16"     # float16 for GPU, int8 for CPU

# ─── Lazy-loaded model ────────────────────────────────────────────────────────
_model = None


def _get_model():
    """Load model once and reuse."""
    global _model
    if _model is not None:
        return _model

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError("faster-whisper not installed. Run: pip install faster-whisper")

    print(f"[STT] Loading faster-whisper model '{WHISPER_MODEL}' on {DEVICE}...")

    try:
        _model = WhisperModel(WHISPER_MODEL, device=DEVICE, compute_type=COMPUTE_TYPE)
        print(f"[STT] Model loaded on {DEVICE}.")
    except Exception:
        # Fall back to CPU if CUDA fails
        print(f"[STT] GPU not available, falling back to CPU...")
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        print("[STT] Model loaded on CPU.")

    return _model


def record_audio() -> str | None:
    """Record from mic, save to temp WAV, return file path."""
    try:
        import sounddevice as sd
        import soundfile as sf
    except ImportError:
        print("[STT] Run: pip install sounddevice soundfile")
        return None

    print(f"Listening for {RECORD_SECONDS} seconds... speak now!")

    try:
        audio = sd.rec(
            int(RECORD_SECONDS * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
        )
        sd.wait()
    except Exception as e:
        print(f"[STT] Recording failed: {e}")
        return None

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, SAMPLE_RATE)
    return tmp.name


def transcribe(wav_path: str) -> str:
    """Transcribe a WAV file using faster-whisper."""
    try:
        model = _get_model()
    except ImportError as e:
        print(f"[STT] {e}")
        return ""

    try:
        segments, info = model.transcribe(
            wav_path,
            language="en",
            beam_size=5,
            vad_filter=True,           # skip silent sections automatically
            vad_parameters=dict(
                min_silence_duration_ms=500
            ),
        )

        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text

    except Exception as e:
        print(f"[STT] Transcription failed: {e}")
        return ""
    finally:
        try:
            os.unlink(wav_path)
        except Exception:
            pass


def listen() -> str:
    """Full pipeline: record -> transcribe -> return text."""
    wav_path = record_audio()
    if not wav_path:
        return ""

    print("Transcribing...")
    text = transcribe(wav_path)

    if text:
        print(f"You said: {text}")
    else:
        print("[STT] Could not transcribe. Please try again.")

    return text