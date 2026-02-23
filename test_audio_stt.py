import os
import json
import wave
import sys
from pathlib import Path

# Try to import Vosk
try:
    from vosk import Model, KaldiRecognizer, SetLogLevel
    SetLogLevel(-1)  # Reduce Vosk logging
except ImportError:
    print("Error: Vosk is not installed. Please install it with 'pip install vosk'.")
    sys.exit(1)

import math
import struct

def get_audio_metrics(wf):
    """Calculate RMS and Peak amplitude from a wave file."""
    try:
        wf.rewind()
        frames = wf.readframes(wf.getnframes())
        
        # Unpack 16-bit PCM data
        samples = struct.unpack(f'<{len(frames)//2}h', frames)
        
        if not samples:
            return 0, 0, 0
        
        # Peak amplitude (0.0 to 1.0)
        peak = max(abs(s) for s in samples) / 32768.0
        
        # RMS amplitude
        sum_sq = sum(float(s * s) for s in samples)
        rms = math.sqrt(sum_sq / len(samples)) / 32768.0
        
        # RMS in Decibels (dBFS)
        if rms > 0:
            dbfs = 20 * math.log10(rms)
        else:
            dbfs = -96.0
            
        return peak, rms, dbfs
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return 0, 0, 0

def transcribe_file(model, audio_path):
    """Transcribe a single WAV file and return text + metrics."""
    metrics = {"peak": 0, "rms": 0, "dbfs": 0, "status": "OK"}
    try:
        with wave.open(str(audio_path), "rb") as wf:
            # Validate audio format
            if wf.getnchannels() != 1:
                return "Error: Mono required", metrics
            if wf.getsampwidth() != 2:
                return "Error: 16-bit PCM required", metrics
            
            # Calculate quality metrics
            peak, rms, dbfs = get_audio_metrics(wf)
            metrics.update({"peak": peak, "rms": rms, "dbfs": dbfs})
            
            if dbfs < -30:
                metrics["status"] = "TOO QUIET"
            elif peak > 0.98:
                metrics["status"] = "CLIPPING"
            
            wf.rewind()
            sample_rate = wf.getframerate()
            recognizer = KaldiRecognizer(model, sample_rate)
            recognizer.SetWords(True)
            
            full_text = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result.get('text'):
                        full_text.append(result['text'])
            
            final_result = json.loads(recognizer.FinalResult())
            if final_result.get('text'):
                full_text.append(final_result['text'])
            
            return ' '.join(full_text).strip(), metrics
    except Exception as e:
        return f"Error: {str(e)}", metrics

def main():
    # Define paths
    base_dir = Path(__file__).parent.absolute()
    model_path = base_dir / 'models' / 'vosk-model-small-en-us-0.15'
    uploads_dir = base_dir / 'media' / 'uploads'
    
    print("=== Audio STT & Quality Test Script ===")
    
    # Check model
    if not model_path.exists():
        print(f"Error: Vosk model not found at {model_path}")
        return

    print(f"Loading model from: {model_path}...")
    try:
        model = Model(str(model_path))
    except Exception as e:
        print(f"Failed to load Vosk model: {e}")
        return

    # Process files
    if not uploads_dir.exists():
        print(f"Error: Uploads directory not found at {uploads_dir}")
        return

    wav_files = sorted(list(uploads_dir.glob("*.wav")))
    
    if not wav_files:
        print("No .wav files found in media/uploads.")
        return

    print(f"Found {len(wav_files)} WAV files. Processing...\n")
    print(f"{'Filename':<25} | {'Peak':<6} | {'RMS(dB)':<8} | {'Status':<10} | {'Transcription'}")
    print("-" * 110)

    for wav_path in wav_files:
        transcription, metrics = transcribe_file(model, wav_path)
        if not transcription:
            transcription = "[...]"
        
        print(f"{wav_path.name:<25} | {metrics['peak']:<6.2f} | {metrics['dbfs']:<8.1f} | {metrics['status']:<10} | {transcription}")

    print("\n=== Test Completed ===")

if __name__ == "__main__":
    main()
