import os
import tempfile
import subprocess
from pathlib import Path

# Import centralized configuration
from config import FFMPEG_PATH

# Set FFmpeg path
os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ['PATH']

# ----------------------#
# Helper: Run FFmpeg    #
# ----------------------#
def run_ffmpeg_command(command):
    """Run FFmpeg and show full error logs if it fails."""
    print(f"[DEBUG] Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] FFmpeg failed with return code {e.returncode}")
        print(f"[ERROR] stdout: {e.stdout}")
        print(f"[ERROR] stderr: {e.stderr}")
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
    lf = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w')
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
    output_path: str = None,
    method: str = "learning_a",
    external_audio_path: str = None
) -> str:
    """
    Crop video segments and merge them into a single video.
    Returns the path to the generated teaser file.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    video_name = Path(video_path).stem  # Get the base filename without extension
    video_ext = Path(video_path).suffix  # Get the extension (e.g., .mp4)
    output_path = output_path or f"{video_name}_teaser{video_ext}"

    _validate_timestamps(timestamps)  # keep the exact order provided (no sorting!)
    temp_segment_paths = []

    if method in ["learning_a", "cinematic_a", "gemini"]:
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

    # Cleanup temp segments
    for p in temp_segment_paths:
        if os.path.exists(p):
            os.remove(p)

    return output_path  # Return only the local path