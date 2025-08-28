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

# ----------------------#
# Initialize S3 Client  #
# ----------------------#
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
# Core helper utilities #
# ----------------------#
def _validate_timestamps(timestamps):
    if not timestamps:
        raise ValueError("timestamps list is empty.")
    for i, pair in enumerate(timestamps):
        if not (isinstance(pair, (list, tuple)) and len(pair) == 2):
            raise ValueError(f"timestamps[{i}] must be [start, end].")
        start, end = float(pair[0]), float(pair[1])
        if end <= start:
            raise ValueError(f"timestamps[{i}] has non-positive duration: {pair}")

def _write_concat_list(paths):
    lf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    with open(lf.name, "w") as f:
        for p in paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    return lf.name

def _sum_durations(timestamps):
    return sum(float(e) - float(s) for s, e in timestamps)

# ----------------------#
# Crop + Merge Function #
# ----------------------#
def crop_and_merge_clips_ffmpeg(
    video_path: str,
    timestamps: list,
    output_path: str = "merged_output.mp4",
    upload_to_s3: bool = False,
    s3_key: str = None,
    method: str = "learning_a",
    external_audio_path: str = None
) -> dict:
    """
    Crop video segments and merge them into a single video.

    Methods:
      - 'learning_a' / 'cinematic_a': keep original audio per clip, then concat.
      - 'learning_b': make video-only clips (in given order), concat them,
                      then add the single external audio once to the final video
                      (trim/pad so it never loops).
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")

    _validate_timestamps(timestamps)  # keep the exact order provided (no sorting!)
    temp_segment_paths = []

    if method in ["learning_a", "cinematic_a"]:
        # Make A/V clips per timestamp (preserve original audio), then concat.
        for idx, (start, end) in enumerate(timestamps):
            print(f"[INFO] Cutting A/V clip {idx+1}/{len(timestamps)}: {start}-{end}s")
            seg = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            temp_segment_paths.append(seg)
            run_ffmpeg_command([
                "ffmpeg", "-y",
                "-ss", str(start),
                "-to", str(end),
                "-i", video_path,
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                "-c:a", "aac",
                "-movflags", "+faststart",
                seg
            ])

        # Concat the A/V clips (re-encode to guarantee compatibility).
        list_file = _write_concat_list(temp_segment_paths)
        print("[INFO] Merging A/V clips...")
        run_ffmpeg_command([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac",
            output_path
        ])

        if os.path.exists(list_file):
            os.remove(list_file)

    elif method == "learning_b":
        if not external_audio_path or not os.path.exists(external_audio_path):
            raise ValueError("For 'learning_b', a valid external_audio_path must be provided.")

        # 1) Make VIDEO-ONLY clips in the EXACT given order.
        for idx, (start, end) in enumerate(timestamps):
            print(f"[INFO] Cutting VIDEO-ONLY clip {idx+1}/{len(timestamps)}: {start}-{end}s")
            seg = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            temp_segment_paths.append(seg)
            run_ffmpeg_command([
                "ffmpeg", "-y",
                "-ss", str(start),
                "-to", str(end),
                "-i", video_path,
                "-an",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "18",
                seg
            ])

        # 2) Concat video-only segments.
        list_file = _write_concat_list(temp_segment_paths)
        concat_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        print("[INFO] Concatenating VIDEO-ONLY clips...")
        run_ffmpeg_command([
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_file,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            concat_video
        ])
        if os.path.exists(list_file):
            os.remove(list_file)

        # 3) Attach the single external audio once:
        #    - If audio is longer than video: stop at end of video (-shortest).
        #    - If audio is shorter: pad with silence (apad) so it does NOT loop.
        total_duration = _sum_durations(timestamps)
        print(f"[INFO] Final video duration (sum of clips): ~{total_duration:.2f}s")
        run_ffmpeg_command([
            "ffmpeg", "-y",
            "-i", concat_video,
            "-i", external_audio_path,
            "-filter_complex", f"[1:a]apad=pad_dur={total_duration}[aud]",
            "-map", "0:v:0", "-map", "[aud]",
            "-c:v", "copy",   # keep the concatenated video as-is
            "-c:a", "aac",
            "-shortest",      # cut audio if it's longer than video
            output_path
        ])
        if os.path.exists(concat_video):
            os.remove(concat_video)

    else:
        raise ValueError(f"Unknown method: {method}")

    print(f"[INFO] Final video saved: {os.path.abspath(output_path)}")

    # Optional upload
    s3_url = None
    if upload_to_s3:
        if not s3_key:
            s3_key = os.path.basename(output_path)
        s3_url = upload_file_to_s3(output_path, s3_key)

    # Cleanup temp segments
    for p in temp_segment_paths:
        if os.path.exists(p):
            os.remove(p)

    return {"local_path": os.path.abspath(output_path), "s3_url": s3_url}


# ----------------------#
# Example usage         #
# ----------------------#
if __name__ == "__main__":
    timestamps = [[22.57, 24.07], [137.47, 138.97], [47.47, 48.97], [53.03, 54.53], [129.2, 130.7], [204.23, 205.73], [27.9, 29.4], [35.17, 36.67], [43.8, 45.3], [83.63, 85.13], [97.33, 98.83], [40.87, 42.37], [54.4, 55.9], [101.2, 102.7], [43.17, 44.67], [44.87, 46.37], [256.73, 258.23], [6.47, 7.97], [8.47, 9.97]]

    result = crop_and_merge_clips_ffmpeg(
        video_path=r"P:/cts npn/practise/Terminator 2_ Judgment Day movie review.mp4",
        timestamps=timestamps,                  # order preserved exactly as provided
        output_path="final_output.mp4",
        upload_to_s3=False,
        s3_key="teasers/final_output.mp4",
        method="learning_b",                    # or 'learning_a' / 'cinematic_a'
        external_audio_path=r"P:/cts npn/summary_audio.mp3"
    )
    print(f"[RESULT] Local file: {result['local_path']}")
    if result['s3_url']:
        print(f"[RESULT] Uploaded to: {result['s3_url']}")
