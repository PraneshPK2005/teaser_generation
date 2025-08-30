# get_videos_from_url.py
import boto3
import os
import yt_dlp
import subprocess
import sys
import shutil
from pathlib import Path

# Import centralized configuration
from config import FFMPEG_PATH, AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, BUCKET_NAME, DOWNLOAD_DIR

# Set FFmpeg path
os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ['PATH']

# Verify ffmpeg exists
try:
    subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

def download_youtube_video_and_audio(url: str, download_dir: str = DOWNLOAD_DIR) -> tuple:
    """
    Download video in 360p and extract optimized audio as WAV for Whisper transcription.
    Returns a tuple (local_video_path, local_audio_path)
    """
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    print(f"[INFO] Downloading video from YouTube: {url}")
    
    output_path = os.path.join(download_dir, "%(title)s.%(ext)s")
    
    ydl_opts = {
        "format": "best[height<=360][ext=mp4]",
        "outtmpl": output_path,
        "merge_output_format": "mp4",
        "quiet": False,
        "restrictfilenames": True,
        "ffmpeg_location": FFMPEG_PATH
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_filename = ydl.prepare_filename(info_dict)
        
        # Extract optimized audio for Whisper
        audio_filename = os.path.splitext(video_filename)[0] + "_whisper.wav"
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", video_filename,
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
    except Exception as e:
        print(f"[ERROR] YouTube download failed: {e}")
        raise

# Rest of the functions remain the same but use config imports

def process_uploaded_video(video_path: str, download_dir: str = "downloads") -> tuple:
    """
    Process an uploaded video file: copy to download directory and extract audio.
    Returns a tuple (local_video_path, local_audio_path)
    """
    Path(download_dir).mkdir(parents=True, exist_ok=True)
    
    # Copy the uploaded video to the download directory
    video_filename = os.path.join(download_dir, os.path.basename(video_path))
    shutil.copy2(video_path, video_filename)
    
    # Extract optimized audio for Whisper
    audio_filename = os.path.splitext(video_filename)[0] + "_whisper.wav"
    ffmpeg_cmd = [
        FFMPEG_PATH, "-y", "-i", video_filename,
        "-vn",                 # no video
        "-acodec", "pcm_s16le", # 16-bit PCM
        "-ar", "16000",         # 16 kHz sample rate
        "-ac", "1",             # mono
        audio_filename
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    
    print(f"[INFO] Video processed: {video_filename}")
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

def handle_video_input(input_source: str, is_youtube: bool = True):
    """
    Handle either YouTube URL or uploaded video file.
    Download/process video + audio and upload both to S3.
    Returns a tuple (video_path, audio_path, video_s3_url, audio_s3_url)
    """
    if is_youtube:
        local_video, local_audio = download_youtube_video_and_audio(input_source)
    else:
        local_video, local_audio = process_uploaded_video(input_source)
    
    # Upload video
    video_s3_key = f"videos/{os.path.basename(local_video)}"
    video_s3_url = upload_file_to_s3(local_video, video_s3_key)
    
    # Upload audio
    audio_s3_key = f"audios/{os.path.basename(local_audio)}"
    audio_s3_url = upload_file_to_s3(local_audio, audio_s3_key)
    
    return local_video, local_audio, video_s3_url, audio_s3_url

# ---------------- Example usage ----------------
if __name__ == "__main__":
    # Example 1: YouTube URL
    youtube_url = "https://youtu.be/DwbAW8G-57A?si=OWdY3QYwsTuFxIo6"
    video_path, audio_path, video_s3, audio_s3 = handle_video_input(youtube_url, is_youtube=True)
    print(f"YouTube video processed: {video_path}, {audio_path}")
    print(f"S3 URLs: {video_s3}, {audio_s3}")
    
    # Example 2: Uploaded file
    # uploaded_file_path = "/path/to/uploaded/video.mp4"
    # video_path, audio_path, video_s3, audio_s3 = handle_video_input(uploaded_file_path, is_youtube=False)
    # print(f"Uploaded video processed: {video_path}, {audio_path}")
    # print(f"S3 URLs: {video_s3}, {audio_s3}")