import ffmpeg
import os
import tempfile
import subprocess
from dotenv import load_dotenv
import boto3

# ----------------------#
# Load environment vars #
# ----------------------#
load_dotenv()
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# ----------------------#
# Upload to S3 function #
# ----------------------#
def upload_file_to_s3(local_file_path: str, s3_key: str) -> str:
    print(f"[INFO] Uploading {local_file_path} to s3://{BUCKET_NAME}/{s3_key}")
    s3_client.upload_file(local_file_path, BUCKET_NAME, s3_key)
    s3_url = f"s3://{BUCKET_NAME}/{s3_key}"
    print(f"[INFO] Upload successful: {s3_url}")
    return s3_url

# ----------------------#
# Helper: Run FFmpeg    #
# ----------------------#
def run_ffmpeg_command(command):
    """Run FFmpeg and show full error logs if it fails."""
    print(f"[DEBUG] Running command: {' '.join(command)}")
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg failed:\n{e.stderr.decode()}")
        raise

# ----------------------#
# Crop + Merge Function #
# ----------------------#
def crop_and_merge_clips_ffmpeg(
    video_path: str,
    timestamps: list,
    output_path: str = "merged_output.mp4",
    upload_to_s3: bool = False,
    s3_key: str = None
) -> dict:
    """
    Crop video segments and merge them using FFmpeg.
    """
    temp_files = []

    # Step 1: Create temporary clips
    for idx, (start, end) in enumerate(timestamps):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        temp_files.append(temp_file)
        print(f"[INFO] Cutting clip {idx + 1}/{len(timestamps)}: {start}-{end}s")
        run_ffmpeg_command([
            "ffmpeg", "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", video_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            temp_file
        ])

    # Step 2: Create list file for merging
    list_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name
    with open(list_file, 'w') as f:
        for temp_file in temp_files:
            f.write(f"file '{os.path.abspath(temp_file)}'\n")

    # Step 3: Merge clips
    print("[INFO] Merging all clips into final output...")
    run_ffmpeg_command([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path
    ])

    print(f"[INFO] Final video saved locally at: {os.path.abspath(output_path)}")

    # Step 4: Optional upload to S3
    s3_url = None
    if upload_to_s3:
        if not s3_key:
            s3_key = os.path.basename(output_path)
        s3_url = upload_file_to_s3(output_path, s3_key)

    # Step 5: Cleanup temp files
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    if os.path.exists(list_file):
        os.remove(list_file)

    return {"local_path": os.path.abspath(output_path), "s3_url": s3_url}

# ----------------------#
# Example usage         #
# ----------------------#
if __name__ == "__main__":
    timestamps = [[11.52, 13.16], [22.4, 27.47], [42.82, 45.58], [47.5, 51.14], [55.14, 57.4], [62.18, 64.2], [78.42, 82.74], [86.12, 89.5], [96.68, 97.26], [104.52, 107.44], [113.32, 116.4], [124.17, 127.2], [129.04, 131.44], [136.18, 137.38], [142.64, 146.24], [147.76, 151.42], [154.73, 155.5], [160.1, 161.46], [168.72, 170.12], [173.02, 176.86], [180.76, 184.5], [186.76, 189.74], [194.58, 198.38], [199.46, 200.6], [202.96, 204.18], [206.98, 210.46]]

    result = crop_and_merge_clips_ffmpeg(
        "P:\cts npn\practise\Terminator 2_ Judgment Day movie review.mp4",
        timestamps,
        "final_output.mp4",
        upload_to_s3=False,
        s3_key="teasers/final_output.mp4"
    )
    print(f"[RESULT] Local file: {result['local_path']}")
    if result['s3_url']:
        print(f"[RESULT] Uploaded to: {result['s3_url']}")
