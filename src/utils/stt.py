"""
Speech-to-Text module using OpenAI Whisper (local model).

Supports:
- Transcribing audio bytes (WAV/MP3/etc.) — for Streamlit UI
- Recording from microphone and transcribing — for CLI

Model: "small" by default (~240 MB, good French accuracy).
All processing is local — no API key or internet required.
"""

import io
import logging
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Whisper model cache (loaded once per process)
_whisper_model = None


def load_whisper(model_name: str = "small") -> object:
    """
    Load (and cache) a Whisper model.

    Args:
        model_name: Whisper model size — "tiny", "base", "small" (default), "medium"
                    "small" offers the best speed/accuracy trade-off for French.

    Returns:
        Loaded Whisper model
    """
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            logger.info(f"Loading Whisper model '{model_name}'...")
            _whisper_model = whisper.load_model(model_name)
            logger.info("Whisper model loaded.")
        except ImportError:
            raise ImportError(
                "openai-whisper not installed. Run: pip install openai-whisper"
            )
    return _whisper_model


def transcribe_audio_bytes(
    audio_bytes: bytes,
    model_name: str = "small",
    language: str = "fr",
) -> Optional[str]:
    """
    Transcribe audio from raw bytes (WAV, MP3, etc.).

    Used by the Streamlit UI: st.audio_input() returns bytes that are
    passed directly to this function.

    Args:
        audio_bytes: Raw audio file content
        model_name: Whisper model size
        language: Expected language code (default: "fr" for French)

    Returns:
        Transcribed text, or None on failure
    """
    model = load_whisper(model_name)

    # Write bytes to a temp file — Whisper requires a file path
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path, language=language, fp16=False)
        text = result["text"].strip()
        logger.info(f"Transcribed: '{text}'")
        return text if text else None
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return None
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def transcribe_from_microphone(
    duration: int = 5,
    model_name: str = "small",
    language: str = "fr",
    sample_rate: int = 16000,
) -> Optional[str]:
    """
    Record from microphone and transcribe with Whisper.

    Used by the CLI --voice mode.

    Args:
        duration: Recording duration in seconds (default: 5)
        model_name: Whisper model size
        language: Expected language code
        sample_rate: Audio sample rate (Whisper expects 16kHz)

    Returns:
        Transcribed text, or None on failure
    """
    try:
        import sounddevice as sd
        import soundfile as sf
        import numpy as np
    except ImportError:
        raise ImportError(
            "sounddevice and soundfile required for microphone input.\n"
            "Run: pip install sounddevice soundfile"
        )

    print(f"  Enregistrement ({duration}s)... Parlez maintenant.")
    try:
        audio = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
    except Exception as e:
        logger.error(f"Microphone recording failed: {e}")
        print(f"  [ERREUR] Enregistrement impossible: {e}")
        return None

    print("  Transcription en cours...")

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio, sample_rate)
        tmp_path = tmp.name

    try:
        model = load_whisper(model_name)
        result = model.transcribe(tmp_path, language=language, fp16=False)
        text = result["text"].strip()
        return text if text else None
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return None
    finally:
        Path(tmp_path).unlink(missing_ok=True)
