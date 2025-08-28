import os
import sys
from pathlib import Path
from typing import List, Tuple
import boto3
from dotenv import load_dotenv

# Import your custom modules
from get_videos_from_url import download_youtube_video_and_audio, upload_file_to_s3, handle_youtube_upload
from transcribe_audio_from_whisper import transcribe_audio
from based_on_orig_transcripts import get_teaser_timestamps
from making_teaser_from_timestamps import crop_and_merge_clips_ffmpeg

# Load environment variables
load_dotenv()

class TeaserGenerator:
    def __init__(self):
        # Initialize S3 client
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.bucket_name = os.getenv("BUCKET_NAME")
        
        # Create directories for outputs
        self.download_dir = "downloads"
        self.output_dir = "outputs"
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def process_youtube_video(self, youtube_url: str, expected_time: int = 45, max_sec: int = 65) -> dict:
        """
        Main function to process a YouTube video and generate a teaser
        
        Args:
            youtube_url: URL of the YouTube video
            expected_time: Minimum teaser duration in seconds
            max_sec: Maximum teaser duration in seconds
            
        Returns:
            Dictionary with paths and URLs of generated assets
        """
        result = {
            "video_path": None,
            "audio_path": None,
            "transcription": None,
            "timestamps": None,
            "teaser_path": None,
            "teaser_s3_url": None
        }
        
        try:
            print(f"Step 1: Downloading video from {youtube_url}")
            # Download video and audio
            video_path, audio_path = download_youtube_video_and_audio(youtube_url, self.download_dir)
            result["video_path"] = video_path
            result["audio_path"] = audio_path
            
            print("Step 2: Uploading to S3")
            # Upload to S3
            video_filename = os.path.basename(video_path)
            audio_filename = os.path.basename(audio_path)
            
            video_s3_key = f"videos/{video_filename}"
            audio_s3_key = f"audios/{audio_filename}"
            
            upload_file_to_s3(video_path, video_s3_key)
            upload_file_to_s3(audio_path, audio_s3_key)
            
            print("Step 3: Transcribing audio")
            # Transcribe audio
            transcription = transcribe_audio(audio_path)
            result["transcription"] = transcription
            
            print("Step 4: Generating teaser timestamps")
            # Generate teaser timestamps
            timestamps = get_teaser_timestamps(transcription, expected_time, max_sec)
            result["timestamps"] = timestamps
            
            # Calculate total duration for verification
            total_duration = sum(end - start for start, end in timestamps)
            print(f"Selected {len(timestamps)} segments with total duration: {total_duration:.2f}s")
            
            print("Step 5: Creating teaser video")
            # Create teaser video
            teaser_filename = f"teaser_{os.path.splitext(video_filename)[0]}.mp4"
            teaser_path = os.path.join(self.output_dir, teaser_filename)
            
            teaser_result = crop_and_merge_clips_ffmpeg(
                video_path=video_path,
                timestamps=timestamps,
                output_path=teaser_path,
                upload_to_s3=True,
                s3_key=f"teasers/{teaser_filename}"
            )
            
            result["teaser_path"] = teaser_result["local_path"]
            result["teaser_s3_url"] = teaser_result["s3_url"]
            
            print(f"Teaser generation complete! Saved to: {teaser_result['local_path']}")
            if teaser_result["s3_url"]:
                print(f"Uploaded to S3: {teaser_result['s3_url']}")
                
        except Exception as e:
            print(f"Error processing video: {e}")
            import traceback
            traceback.print_exc()
            
        return result
    
    def process_local_video(self, video_path: str, expected_time: int = 45, max_sec: int = 65) -> dict:
        """
        Process a local video file and generate a teaser
        
        Args:
            video_path: Path to the local video file
            expected_time: Minimum teaser duration in seconds
            max_sec: Maximum teaser duration in seconds
            
        Returns:
            Dictionary with paths and URLs of generated assets
        """
        result = {
            "video_path": video_path,
            "audio_path": None,
            "transcription": None,
            "timestamps": None,
            "teaser_path": None,
            "teaser_s3_url": None
        }
        
        try:
            # Extract audio from video
            print("Step 1: Extracting audio from video")
            audio_filename = os.path.splitext(os.path.basename(video_path))[0] + "_whisper.wav"
            audio_path = os.path.join(self.download_dir, audio_filename)
            
            # Use FFmpeg to extract audio
            import subprocess
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-vn",                 # no video
                "-acodec", "pcm_s16le", # 16-bit PCM
                "-ar", "16000",         # 16 kHz sample rate
                "-ac", "1",             # mono
                audio_path
            ]
            subprocess.run(ffmpeg_cmd, check=True)
            
            result["audio_path"] = audio_path
            
            print("Step 2: Uploading to S3")
            # Upload to S3
            video_filename = os.path.basename(video_path)
            audio_filename = os.path.basename(audio_path)
            
            video_s3_key = f"videos/{video_filename}"
            audio_s3_key = f"audios/{audio_filename}"
            
            upload_file_to_s3(video_path, video_s3_key)
            upload_file_to_s3(audio_path, audio_s3_key)
            
            print("Step 3: Transcribing audio")
            # Transcribe audio
            transcription = transcribe_audio(audio_path)
            result["transcription"] = transcription
            
            print("Step 4: Generating teaser timestamps")
            # Generate teaser timestamps
            timestamps = get_teaser_timestamps(transcription, expected_time, max_sec)
            result["timestamps"] = timestamps
            
            # Calculate total duration for verification
            total_duration = sum(end - start for start, end in timestamps)
            print(f"Selected {len(timestamps)} segments with total duration: {total_duration:.2f}s")
            
            print("Step 5: Creating teaser video")
            # Create teaser video
            teaser_filename = f"teaser_{os.path.splitext(video_filename)[0]}.mp4"
            teaser_path = os.path.join(self.output_dir, teaser_filename)
            
            teaser_result = crop_and_merge_clips_ffmpeg(
                video_path=video_path,
                timestamps=timestamps,
                output_path=teaser_path,
                upload_to_s3=True,
                s3_key=f"teasers/{teaser_filename}"
            )
            
            result["teaser_path"] = teaser_result["local_path"]
            result["teaser_s3_url"] = teaser_result["s3_url"]
            
            print(f"Teaser generation complete! Saved to: {teaser_result['local_path']}")
            if teaser_result["s3_url"]:
                print(f"Uploaded to S3: {teaser_result['s3_url']}")
                
        except Exception as e:
            print(f"Error processing video: {e}")
            import traceback
            traceback.print_exc()
            
        return result

def main():
    """
    Main function to demonstrate the teaser generation process
    """
    generator = TeaserGenerator()
    
    # Example usage with YouTube URL
    youtube_url = "https://youtu.be/DwbAW8G-57A?si=OWdY3QYwsTuFxIo6"
    expected_time = 45
    max_sec = 65
    
    print("Starting YouTube video processing...")
    result = generator.process_youtube_video(youtube_url, expected_time, max_sec)
    
    # Print results
    print("\n=== PROCESSING RESULTS ===")
    print(f"Original video: {result.get('video_path', 'N/A')}")
    print(f"Extracted audio: {result.get('audio_path', 'N/A')}")
    print(f"Teaser created: {result.get('teaser_path', 'N/A')}")
    print(f"Teaser S3 URL: {result.get('teaser_s3_url', 'N/A')}")
    
    # Example with local video file
    # local_video_path = "path/to/your/local/video.mp4"
    # print("\nStarting local video processing...")
    # result = generator.process_local_video(local_video_path, expected_time, max_sec)

if __name__ == "__main__":
    main()