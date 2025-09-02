# gemini_for_timestamps.py
import google.generativeai as genai
import os
import time
import re
import subprocess
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Please create a .env file and add it.")

genai.configure(api_key=api_key)

# --- Function: Get Video Duration ---
def get_video_duration(video_path):
    """Gets the duration of a video file in seconds using the ffprobe OS command."""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except subprocess.CalledProcessError as e:
        print(f"Error getting video duration: {e.stderr}")
        return 0
    except FileNotFoundError:
        print("Error: ffprobe command not found. Please ensure FFmpeg is installed and in your system's PATH.")
        return 0

# --- Function: Split Video into Chunks ---
def split_video_into_chunks(input_path, output_dir="video_chunks", chunk_duration=1800):
    """Splits a video into 30-minute (1800s) chunks using the ffmpeg OS command."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_pattern = os.path.join(output_dir, 'chunk-%03d.mp4')

    command = [
        'ffmpeg',
        '-i', input_path,
        '-c', 'copy',
        '-f', 'segment',
        '-segment_time', str(chunk_duration),
        '-reset_timestamps', '1',
        '-y',  # Overwrite output files without asking
        output_pattern
    ]
    
    try:
        print(f"Running FFmpeg command: {' '.join(command)}")
        # Use capture_output to get stderr in case of an error
        subprocess.run(command, check=True, capture_output=True, text=True)
        
        chunk_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.startswith('chunk-') and f.endswith('.mp4')]
        chunk_files.sort()
        print(f"Video split into {len(chunk_files)} chunks.")
        return chunk_files
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during video splitting: {e.stderr}")
        return []
    except FileNotFoundError:
        print("Error: ffmpeg command not found. Please ensure FFmpeg is installed and in your system's PATH.")
        return []

# --- Function: Parse Gemini Response to Timestamps ---
def parse_gemini_response(response_text, offset_seconds=0):
    """
    Parses the Gemini response text and converts it to a list of timestamp pairs.
    
    Expected format:
    [MM:SS - MM:SS] Description text
    
    Returns:
    list: List of [start, end] pairs in seconds (format expected by crop_and_merge_clips_ffmpeg)
    """
    timestamps = []
    pattern = r"\[(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\].*"
    
    for line in response_text.split('\n'):
        match = re.match(pattern, line)
        if match:
            try:
                start_min, start_sec, end_min, end_sec = map(int, match.groups())
                start_time = start_min * 60 + start_sec + offset_seconds
                end_time = end_min * 60 + end_sec + offset_seconds
                
                # Return as [start, end] pair (format expected by crop_and_merge_clips_ffmpeg)
                timestamps.append([start_time, end_time])
            except ValueError:
                print(f"Could not parse timestamp: {line}")
                continue
    
    return timestamps

# --- Function: Convert seconds to MM:SS format ---
def seconds_to_mmss(seconds):
    """Convert seconds to MM:SS format."""
    minutes = int(seconds) // 60
    seconds = int(seconds) % 60
    return f"{minutes:02d}:{seconds:02d}"

# --- Main Function to Generate Timestamps with Gemini ---
def generate_timestamps_with_gemini(video_path, max_length=70, min_length=60):
    """
    Main function to generate timestamps using Gemini.
    
    Args:
        video_path (str): Path to the video file
        max_length (int): Maximum teaser duration in seconds
        min_length (int): Minimum teaser duration in seconds
    
    Returns:
        tuple: (timestamps, total_duration)
               timestamps: List of [start, end] pairs in seconds
               total_duration: Sum of all clip durations
    """
    chunk_duration_seconds = 1800  # 30 minutes

    duration = get_video_duration(video_path)
    
    # If the video is longer than 30 mins, split it. Otherwise, process the whole file.
    if duration > chunk_duration_seconds:
        print("Video is longer than 30 minutes. Splitting into chunks...")
        chunk_paths = split_video_into_chunks(video_path, chunk_duration=chunk_duration_seconds)
    else:
        chunk_paths = [video_path]
        print("Video is 30 minutes or less. Processing as a single file.")
        
    all_timestamps = []
    
    for i, path in enumerate(chunk_paths):
        offset = i * chunk_duration_seconds
        print(f"\n--- Processing Chunk {i+1}/{len(chunk_paths)} ---")
        
        # 1. Upload the Video Chunk
        print(f"Uploading file: {path}...")
        try:
            video_file = genai.upload_file(path=path, display_name=f"chunk_{i+1}")
            print(f"Uploaded file '{video_file.display_name}' as: {video_file.name}")
        except Exception as e:
            print(f"Error uploading chunk {i+1}: {e}")
            continue

        # 2. Wait for processing
        print("Waiting for file processing...")
        while video_file.state.name == "PROCESSING":
            time.sleep(10)
            video_file = genai.get_file(name=video_file.name)
            print(f"File state: {video_file.state.name}")

        if video_file.state.name == "FAILED":
            print(f"Video processing failed for chunk {i+1}. Skipping.")
            continue
        
        print("✅ File is now ACTIVE and ready to use.")

        # 3. Ask a Question About the Video Chunk
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        
        # Convert seconds to MM:SS format for the prompt
        min_duration_mmss = seconds_to_mmss(min_length)
        max_duration_mmss = seconds_to_mmss(max_length)
        
        prompt = f"""Analyze this video and identify the most compelling and essential moments for a short promotional teaser. 
The teaser should be between {min_duration_mmss} and {max_duration_mmss} long (approximately {min_length}-{max_length} seconds).

For each key moment, provide a brief, one-sentence description of the event. Your output must follow this exact format, with timestamps indicating the start and end of the clip, with no additional text, explanations, or conversational filler:
[MM:SS - MM:SS] A brief description of the action.

Example Output for a short video:
[00:15 - 00:20] A character's facial expression changes from fear to determination.
[00:45 - 00:55] The main hero dodges a series of incoming laser blasts.
[01:10 - 01:25] A final confrontation with the villain on a rooftop, with a dramatic reveal.

Example Output for a long video:
[05:30 - 05:40] The protagonist makes a crucial discovery in a library.
[12:15 - 12:25] A tense conversation with a rival reveals a key plot point.
[27:50 - 28:10] An unexpected explosion and subsequent chase scene.
[45:05 - 45:20] The emotional climax of the story is revealed through dialogue.

IMPORTANT: 
1. The total duration of all selected clips should be between {min_length} and {max_length} seconds.
2. You MUST provide at least one timestamp in the exact format shown above.
3. Do not include any other text in your response besides the timestamps and descriptions."""

        try:
            response = model.generate_content([prompt, video_file])
            print(f"Gemini response: {response.text}")
            
            # 4. Parse the response and adjust timestamps with offset
            chunk_timestamps = parse_gemini_response(response.text, offset)
            all_timestamps.extend(chunk_timestamps)
            
            if not chunk_timestamps:
                print("Warning: No timestamps found in Gemini response for this chunk.")
                
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            continue

        # 5. Clean Up Uploaded File
        print(f"\nDeleting uploaded file: {video_file.name}")
        genai.delete_file(video_file.name)
        print("File deleted.")
    
    # 6. Calculate total duration
    total_duration = sum(end - start for start, end in all_timestamps) if all_timestamps else 0
    
    # 7. Check if we have any timestamps
    if not all_timestamps:
        raise ValueError("No timestamps were generated from the video. Gemini did not return any valid timestamps.")
    
    # 8. Clean up the local chunk files
    if duration > chunk_duration_seconds and chunk_paths:
        print("\nCleaning up local video chunks...")
        for file_path in chunk_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        if os.path.exists("video_chunks"):
            try:
                os.rmdir("video_chunks")
                print("Local files cleaned up.")
            except OSError as e:
                print(f"Error removing chunk directory: {e}. It might not be empty.")

    return all_timestamps, total_duration

# --- Standalone Execution (if run directly) ---
if __name__ == "__main__":
    # Example video file path
    video_file_path = "Bhoot Raja Aur Ronnie (2012) .mp4" 
    if not os.path.exists(video_file_path):
        print(f"Error: Video file not found at '{video_file_path}'")
    else:
        try:
            timestamps, total_duration = generate_timestamps_with_gemini(video_file_path)
            print("\n--- Final Results ---")
            print(f"Generated {len(timestamps)} timestamps with a total duration of: {total_duration:.2f} seconds")
            for ts in timestamps:
                print(f"  - Clip from {ts[0]:.2f}s to {ts[1]:.2f}s")
        except Exception as e:
            print(f"\nAn error occurred in the main process: {e}")