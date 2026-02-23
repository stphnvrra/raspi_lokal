"""
Text-to-Speech service using pyttsx3 (offline).
Designed for Raspberry Pi with espeak backend.
"""
import logging
import os
import uuid
from pathlib import Path
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import pyttsx3, but allow graceful degradation
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not installed. TTS will be unavailable.")


class TTSService:
    """
    Text-to-Speech service using pyttsx3.
    Uses espeak on Linux/Raspberry Pi for offline TTS.
    """

    def __init__(self):
        self.rate = getattr(settings, 'TTS_RATE', 150)
        self.volume = getattr(settings, 'TTS_VOLUME', 1.0)
        self.output_dir = Path(settings.MEDIA_ROOT) / 'tts'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._engine = None

    def _get_engine(self):
        """Get or create pyttsx3 engine instance."""
        if not PYTTSX3_AVAILABLE:
            raise RuntimeError("pyttsx3 is not installed")
        
        if self._engine is None:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty('rate', self.rate)
                self._engine.setProperty('volume', self.volume)
            except Exception as e:
                logger.error(f"Failed to initialize TTS engine: {e}")
                raise
        
        return self._engine

    @property
    def is_available(self) -> bool:
        """Check if TTS service is available."""
        if not PYTTSX3_AVAILABLE:
            return False
        try:
            self._get_engine()
            return True
        except Exception:
            return False

    def speak(self, text: str) -> bool:
        """
        Speak text directly through connected speaker (blocking).
        
        Args:
            text: The text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            engine = self._get_engine()
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"TTS speak failed: {e}")
            return False

    def generate_audio_file(
        self,
        text: str,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate an audio file from text.
        
        Args:
            text: The text to convert to speech
            filename: Optional custom filename (without extension)
            
        Returns:
            Relative path to generated audio file, or None if failed
        """
        if not PYTTSX3_AVAILABLE:
            logger.error("Cannot generate audio: pyttsx3 not available")
            return None

        import subprocess
        import shutil
        import sys
        
        try:
            # Generate unique filename if not provided
            if not filename:
                filename = f"tts_{uuid.uuid4().hex[:12]}"
            
            # Full path for the audio file
            audio_path = self.output_dir / f"{filename}.wav"
            
            # On macOS, use native 'say' command (pyttsx3 save_to_file is buggy on Mac)
            if sys.platform == 'darwin' and shutil.which('say'):
                temp_m4a = self.output_dir / f"{filename}_temp.m4a"
                
                try:
                    # Use Mac's say command with m4a output (AIFF is buggy)
                    result = subprocess.run([
                        'say', '-o', str(temp_m4a), text
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode != 0:
                        logger.error(f"Mac 'say' command failed: {result.stderr}")
                        raise RuntimeError("say command failed")
                    
                    # Convert m4a to wav using ffmpeg
                    if shutil.which('ffmpeg') and temp_m4a.exists():
                        result = subprocess.run([
                            'ffmpeg', '-y',
                            '-i', str(temp_m4a),
                            '-acodec', 'pcm_s16le',
                            '-ar', '22050',
                            str(audio_path)
                        ], capture_output=True, text=True, timeout=30)
                        
                        temp_m4a.unlink(missing_ok=True)
                        
                        if result.returncode == 0 and audio_path.exists():
                            logger.info(f"Generated TTS audio using Mac 'say': tts/{filename}.wav")
                            return f"tts/{filename}.wav"
                    
                except Exception as e:
                    logger.warning(f"Mac 'say' fallback failed: {e}, trying pyttsx3")
                    temp_m4a.unlink(missing_ok=True) if temp_m4a.exists() else None
            
            # On Linux/Raspberry Pi, use pyttsx3 with espeak (this works correctly)
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)
            
            engine.save_to_file(text, str(audio_path))
            engine.runAndWait()
            
            try:
                engine.stop()
            except:
                pass
            
            # Return relative path from MEDIA_ROOT
            relative_path = f"tts/{filename}.wav"
            
            if audio_path.exists() and audio_path.stat().st_size > 100:  # More than just header
                logger.info(f"Generated TTS audio: {relative_path}")
                return relative_path
            else:
                logger.error(f"Audio file not created or empty: {audio_path}")
                return None
                
        except Exception as e:
            logger.error(f"TTS file generation failed: {e}")
            return None

    def cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Remove old TTS audio files to save disk space.
        
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
            for audio_file in self.output_dir.glob("*.wav"):
                file_age = current_time - audio_file.stat().st_mtime
                if file_age > max_age_seconds:
                    audio_file.unlink()
                    removed += 1
                    
            logger.info(f"Cleaned up {removed} old TTS files")
        except Exception as e:
            logger.error(f"TTS cleanup failed: {e}")
            
        return removed

    def get_voices(self) -> list:
        """
        Get list of available voices.
        
        Returns:
            List of voice dictionaries with id, name, and languages
        """
        try:
            engine = self._get_engine()
            voices = engine.getProperty('voices')
            return [
                {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': voice.languages
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Failed to get voices: {e}")
            return []

    def set_voice(self, voice_id: str) -> bool:
        """
        Set the TTS voice by ID.
        
        Args:
            voice_id: The voice ID to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            engine = self._get_engine()
            engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            logger.error(f"Failed to set voice: {e}")
            return False

    def set_rate(self, rate: int) -> bool:
        """
        Set the speaking rate (words per minute).
        
        Args:
            rate: Words per minute (typically 100-200)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            engine = self._get_engine()
            engine.setProperty('rate', rate)
            self.rate = rate
            return True
        except Exception as e:
            logger.error(f"Failed to set rate: {e}")
            return False


# Singleton instance for easy import
tts_service = TTSService()
