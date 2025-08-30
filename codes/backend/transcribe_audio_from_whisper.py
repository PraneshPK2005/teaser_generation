# transcribe_audio_from_whisper.py
import torch
import whisper_timestamped as whisper
import os

# Import centralized configuration
from config import FFMPEG_PATH

# Set FFmpeg path for whisper
os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ['PATH']

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio using Whisper Timestamped.
    Returns a string of timestamped segments.
    """
    # Verify the audio file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("small", device=DEVICE)
    
    try:
        audio = whisper.load_audio(audio_path)
        result = whisper.transcribe(model, audio)
        
        # Build formatted string of timestamped segments
        timestamped_segments = []

        for segment in result["segments"]:
            timestamp = f"[{segment['start']:.2f}s - {segment['end']:.2f}s]"
            line = f"{timestamp} {segment['text']}"
            timestamped_segments.append(line)

        return timestamped_segments
    except Exception as e:
        print(f"[ERROR] Audio transcription failed: {e}")
        raise