"""Voice Analyzer — Whisper transcription + tone / emotion analysis.

Captures spoken audio, transcribes it, and derives vocal indicators
(energy, pitch, speech-rate) that map to cognitive states.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from backend.utils.logger import log

_whisper_model: Any | None = None


def _get_whisper(model_size: str = "base"):
    """Lazy-load the Whisper model once."""
    global _whisper_model  # noqa: PLW0603
    if _whisper_model is None:
        import whisper

        _whisper_model = whisper.load_model(model_size)
        log.info("whisper.loaded", model=model_size)
    return _whisper_model


@dataclass
class VoiceMetrics:
    """Quantified vocal signals for an audio segment."""

    transcript: str = ""
    language: str = "en"
    energy_db: float = 0.0
    pitch_mean_hz: float = 0.0
    pitch_std_hz: float = 0.0
    speech_rate_wpm: float = 0.0
    pause_ratio: float = 0.0
    tone_label: str = "neutral"  # neutral | fatigued | frustrated | focused


def _compute_energy(audio: np.ndarray) -> float:
    """RMS energy in dB."""
    rms = np.sqrt(np.mean(audio.astype(np.float64) ** 2))
    if rms == 0:
        return -100.0
    return float(20 * np.log10(rms))


def _estimate_pitch(audio: np.ndarray, sr: int = 16000) -> tuple[float, float]:
    """Autocorrelation-based pitch estimation returning (mean_hz, std_hz)."""
    frame_len = min(len(audio), sr // 4)
    if frame_len < 256:
        return 0.0, 0.0
    frame = audio[:frame_len].astype(np.float64)
    corr = np.correlate(frame, frame, mode="full")
    corr = corr[len(corr) // 2 :]
    # Find first peak after the zero-lag
    d = np.diff(corr)
    start = 0
    for i in range(len(d) - 1):
        if d[i] < 0 and d[i + 1] >= 0:
            start = i + 1
            break
    if start == 0 or start >= len(corr):
        return 0.0, 0.0
    peak = start + int(np.argmax(corr[start:]))
    if peak == 0:
        return 0.0, 0.0
    f0 = sr / peak
    return float(f0), 0.0


def _classify_tone(
    energy: float,
    pitch_mean: float,
    speech_rate: float,
    pause_ratio: float,
) -> str:
    """Rule-based tone classifier — lightweight first pass."""
    if energy < -40 and pause_ratio > 0.5:
        return "fatigued"
    if pitch_mean > 250 and speech_rate > 180:
        return "frustrated"
    if 100 < pitch_mean < 200 and speech_rate > 100:
        return "focused"
    return "neutral"


class VoiceAnalyzer:
    """Transcribes audio and extracts vocal metrics."""

    def __init__(self, whisper_model: str = "base", sample_rate: int = 16000) -> None:
        self._model_name = whisper_model
        self._sr = sample_rate

    def analyze_audio(
        self, audio: np.ndarray, *, duration_sec: float | None = None
    ) -> VoiceMetrics:
        """Analyse a raw 16 kHz mono float32 audio array."""
        model = _get_whisper(self._model_name)
        result = model.transcribe(
            audio.astype(np.float32), fp16=False, language=None
        )
        transcript: str = result.get("text", "").strip()
        language: str = result.get("language", "en")

        energy = _compute_energy(audio)
        pitch_mean, pitch_std = _estimate_pitch(audio, self._sr)

        if duration_sec is None:
            duration_sec = len(audio) / self._sr
        word_count = len(transcript.split()) if transcript else 0
        speech_rate = (word_count / (duration_sec / 60.0)) if duration_sec > 0 else 0.0

        # Pause ratio: fraction of silence frames (<-50 dB)
        frame_size = self._sr // 10  # 100 ms frames
        frames = [
            audio[i : i + frame_size] for i in range(0, len(audio), frame_size)
        ]
        silent = sum(1 for f in frames if _compute_energy(f) < -50)
        pause_ratio = silent / len(frames) if frames else 0.0

        tone = _classify_tone(energy, pitch_mean, speech_rate, pause_ratio)

        metrics = VoiceMetrics(
            transcript=transcript,
            language=language,
            energy_db=energy,
            pitch_mean_hz=pitch_mean,
            pitch_std_hz=pitch_std,
            speech_rate_wpm=speech_rate,
            pause_ratio=pause_ratio,
            tone_label=tone,
        )
        log.debug("voice.metrics", tone=tone, energy=energy, wpm=speech_rate)
        return metrics

    def analyze_file(self, path: str | Path) -> VoiceMetrics:
        """Convenience: load a WAV/MP3 and analyse."""
        import whisper

        audio = whisper.load_audio(str(path))
        return self.analyze_audio(audio)
