import boto3
import os
from pathlib import Path
from dotenv import load_dotenv
import yt_dlp
import subprocess
import sys

# ---------------- CONFIG ----------------
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FFMPEG_PATH = r'C:/Users/Pranesh/Downloads/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin'  # optional, Docker may have ffmpeg in PATH

if not FFMPEG_PATH:
    print("[INFO] FFMPEG_PATH not set, using system PATH")
    ffmpeg_exe = "ffmpeg"
else:
    ffmpeg_exe = os.path.join(FFMPEG_PATH, "ffmpeg")

# Verify ffmpeg exists
try:
    subprocess.run([ffmpeg_exe, "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
except Exception as e:
    print(f"[ERROR] ffmpeg not found or not executable: {e}")
    sys.exit(1)

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# ---------------- FUNCTIONS ----------------
def download_youtube_video_and_audio(url: str, download_dir: str = "downloads") -> tuple:
    """
    Download video in 360p and extract optimized audio as WAV for Whisper transcription.
    Returns a tuple (local_video_path, local_audio_path)
    """
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Downloading video from YouTube: {url}")
    
    output_path = os.path.join(download_dir, "%(title)s.%(ext)s")
    
    ydl_opts = {
        "format": "bestvideo[height<=360]+bestaudio/best",
        "outtmpl": output_path,
        "merge_output_format": "mp4",
        "quiet": False,
        "restrictfilenames": True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_filename = ydl.prepare_filename(info_dict)
    
    # Extract optimized audio for Whisper
    audio_filename = os.path.splitext(video_filename)[0] + "_whisper.wav"
    ffmpeg_cmd = [
        ffmpeg_exe, "-y", "-i", video_filename,
        "-vn",                 # no video
        "-acodec", "pcm_s16le", # 16-bit PCM
        "-ar", "16000",         # 16 kHz sample rate
        "-ac", "1",             # mono
        audio_filename
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    
    print(f"[INFO] Video downloaded: {video_filename}")
    print(f"[INFO] Audio extracted for Whisper: {audio_filename}")
    
    return video_filename, audio_filename

def upload_file_to_s3(local_file_path: str, s3_key: str) -> str:
    """
    Upload a local file to S3 at the given key.
    Returns the S3 URL.
    """
    print(f"[INFO] Uploading {local_file_path} to s3://{BUCKET_NAME}/{s3_key}")
    s3_client.upload_file(local_file_path, BUCKET_NAME, s3_key)
    s3_url = f"s3://{BUCKET_NAME}/{s3_key}"
    print(f"[INFO] Upload successful: {s3_url}")
    return s3_url


def handle_youtube_upload(youtube_url: str):
    """
    Download video + audio from YouTube and upload both to S3.
    """
    local_video, local_audio = download_youtube_video_and_audio(youtube_url)
    
    # Upload video
    video_s3_key = f"videos/{os.path.basename(local_video)}"
    upload_file_to_s3(local_video, video_s3_key)
    
    # Upload audio
    audio_s3_key = f"audios/{os.path.basename(local_audio)}"
    upload_file_to_s3(local_audio, audio_s3_key)


# ---------------- Example usage ----------------
if __name__ == "__main__":
    handle_youtube_upload("https://youtu.be/DwbAW8G-57A?si=OWdY3QYwsTuFxIo6")
