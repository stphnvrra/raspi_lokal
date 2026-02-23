"""
Speech-to-Text service using Vosk (offline).
Designed for Raspberry Pi with small English model.
"""
import logging
import os
import json
import wave
from pathlib import Path
from typing import Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import Vosk, but allow graceful degradation
try:
    from vosk import Model, KaldiRecognizer, SetLogLevel
    SetLogLevel(-1)  # Reduce Vosk logging
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("vosk not installed. Speech-to-text will be unavailable.")

# Try to import soundfile for audio conversion
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    logger.warning("soundfile not installed. Audio format conversion may fail.")

# Check for ffmpeg for WebM conversion (browser audio format)
import subprocess
import shutil

FFMPEG_AVAILABLE = shutil.which('ffmpeg') is not None
if not FFMPEG_AVAILABLE:
    logger.warning("ffmpeg not found. WebM audio conversion will be unavailable. Install with: sudo apt-get install ffmpeg")


class STTService:
    """
    Speech-to-Text service using Vosk for offline recognition.
    Uses a small English model suitable for Raspberry Pi.
    """

    def __init__(self):
        self.model_path = getattr(
            settings,
            'VOSK_MODEL_PATH',
            str(Path(settings.BASE_DIR) / 'models' / 'vosk-model-small-en-us-0.15')
        )
        self.upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._model = None

    def _get_model(self):
        """Load or return cached Vosk model."""
        if not VOSK_AVAILABLE:
            raise RuntimeError("Vosk is not installed")
        
        if self._model is None:
            model_path = Path(self.model_path)
            if not model_path.exists():
                logger.error(f"Vosk model not found at: {model_path}")
                raise FileNotFoundError(
                    f"Vosk model not found. Please download it from "
                    f"https://alphacephei.com/vosk/models and extract to {model_path}"
                )
            
            logger.info(f"Loading Vosk model from: {model_path}")
            self._model = Model(str(model_path))
            
        return self._model

    @property
    def is_available(self) -> bool:
        """Check if STT service is available."""
        if not VOSK_AVAILABLE:
            return False
        try:
            self._get_model()
            return True
        except Exception:
            return False

    def transcribe_file(self, audio_file_path: str) -> Tuple[str, bool]:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Tuple of (transcribed_text, success_flag)
        """
        if not VOSK_AVAILABLE:
            return "Speech recognition is not available.", False

        try:
            audio_path = Path(audio_file_path)
            
            # Convert to WAV if needed
            wav_path = self._ensure_wav_format(audio_path)
            
            # Open and transcribe
            model = self._get_model()
            
            with wave.open(str(wav_path), "rb") as wf:
                # Validate audio format
                if wf.getnchannels() != 1:
                    return "Audio must be mono channel.", False
                if wf.getsampwidth() != 2:
                    return "Audio must be 16-bit.", False
                
                sample_rate = wf.getframerate()
                recognizer = KaldiRecognizer(model, sample_rate)
                recognizer.SetWords(True)
                
                # Process audio in chunks
                full_text = []
                while True:
                    data = wf.readframes(4000)
                    if len(data) == 0:
                        break
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if result.get('text'):
                            full_text.append(result['text'])
                
                # Get final result
                final_result = json.loads(recognizer.FinalResult())
                if final_result.get('text'):
                    full_text.append(final_result['text'])
                
                transcribed = ' '.join(full_text).strip()
                
                if transcribed:
                    logger.info(f"Transcribed: {transcribed[:50]}...")
                    return transcribed, True
                else:
                    return "Could not understand the audio. Please speak clearly.", False
                    
        except FileNotFoundError:
            return f"Audio file not found: {audio_file_path}", False
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return f"Transcription error: {str(e)}", False

    def _ensure_wav_format(self, audio_path: Path) -> Path:
        """
        Convert audio to WAV format if needed.
        Supports WebM (browser format), OGG, MP3, and other formats.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Path to WAV file (may be same as input or converted file)
        """
        if audio_path.suffix.lower() == '.wav':
            return audio_path
        
        wav_path = audio_path.with_suffix('.wav')
        
        # Use ffmpeg for WebM, OGG, and other common browser formats
        if audio_path.suffix.lower() in ['.webm', '.ogg', '.mp3', '.m4a', '.opus', '.mp4']:
            if not FFMPEG_AVAILABLE:
                raise RuntimeError(
                    f"Cannot convert {audio_path.suffix} to WAV: ffmpeg not installed. "
                    "Install with: sudo apt-get install ffmpeg"
                )
            
            try:
                # Use ffmpeg to convert to 16kHz mono WAV (optimal for Vosk)
                result = subprocess.run([
                    'ffmpeg',
                    '-y',  # Overwrite output file
                    '-i', str(audio_path),  # Input file
                    '-ar', '16000',  # Sample rate 16kHz
                    '-ac', '1',  # Mono
                    '-acodec', 'pcm_s16le',  # 16-bit PCM
                    str(wav_path)
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    logger.error(f"ffmpeg error: {result.stderr}")
                    raise RuntimeError(f"ffmpeg conversion failed: {result.stderr}")
                
                logger.info(f"Converted {audio_path} to WAV format using ffmpeg")
                return wav_path
                
            except subprocess.TimeoutExpired:
                logger.error("ffmpeg conversion timed out")
                raise RuntimeError("Audio conversion timed out")
            except Exception as e:
                logger.error(f"ffmpeg audio conversion failed: {e}")
                raise RuntimeError(
                    f"Audio conversion failed. Ensure ffmpeg is installed: {e}"
                )
        
        # Fallback to soundfile for other formats
        if not SOUNDFILE_AVAILABLE:
            raise RuntimeError(
                f"Cannot convert {audio_path.suffix} to WAV: soundfile not installed"
            )
        
        try:
            data, samplerate = sf.read(str(audio_path))
            
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = data.mean(axis=1)
            
            # Write as 16-bit WAV
            sf.write(str(wav_path), data, samplerate, subtype='PCM_16')
            
            logger.info(f"Converted {audio_path} to WAV format")
            return wav_path
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {e}")
            raise

    def save_uploaded_audio(self, uploaded_file) -> str:
        """
        Save an uploaded audio file to disk.
        
        Args:
            uploaded_file: Django UploadedFile object
            
        Returns:
            Path to saved file
        """
        import uuid
        
        # Generate unique filename
        ext = Path(uploaded_file.name).suffix or '.wav'
        filename = f"audio_{uuid.uuid4().hex[:12]}{ext}"
        file_path = self.upload_dir / filename
        
        # Save file
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        logger.info(f"Saved uploaded audio: {file_path}")
        return str(file_path)

    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Remove old uploaded audio files to save disk space.
        
        Args:
            max_age_hours: Remove files older than this many hours
            
        Returns:
            Number of files removed
        """
        import time
        removed = 0
        max_age_seconds = max_age_hours * 3600
        current_time = time.time()
        
        try:
            for audio_file in self.upload_dir.glob("*"):
                if audio_file.is_file():
                    file_age = current_time - audio_file.stat().st_mtime
                    if file_age > max_age_seconds:
                        audio_file.unlink()
                        removed += 1
                        
            logger.info(f"Cleaned up {removed} old audio files")
        except Exception as e:
            logger.error(f"Audio cleanup failed: {e}")
            
        return removed


# Singleton instance for easy import
stt_service = STTService()
