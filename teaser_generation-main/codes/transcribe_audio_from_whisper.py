import torch
import whisper_timestamped as whisper

# ---------------- WHISPER TRANSCRIPTION ----------------
def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio using Whisper Timestamped.
    Returns a string of timestamped segments.
    """
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    model = whisper.load_model("small", device=DEVICE)
    
    audio = whisper.load_audio(audio_path)
    result = whisper.transcribe(model, audio)
    
    # Build formatted string of timestamped segments
    timestamped_segments = []

    for segment in result["segments"]:
        timestamp = f"[{segment['start']:.2f}s - {segment['end']:.2f}s]"
        line = f"{timestamp} {segment['text']}"
        timestamped_segments.append(line)

    return timestamped_segments

# ---------------- MAIN ----------------
if __name__ == "__main__":
    audio_path = r"P:\cts npn\youtube_audio.wav"
    transcription_output = transcribe_audio(audio_path)
    print(transcription_output)
