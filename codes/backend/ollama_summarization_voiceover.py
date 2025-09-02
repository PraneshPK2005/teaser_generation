import ollama
import pyttsx3
import os
import re 
import syllables
import subprocess
import shlex
import json

def summarize_text(transcript, duration_seconds, wpm, model='llama3.2:latest'):
    # ... (keep this function unchanged)
    if not transcript: return None
    target_word_count = int((duration_seconds / 60) * wpm)
    print(f"Targeting a summary of approximately {target_word_count} words.")
    prompt = f"""
    Your task is to summarize the following transcript.
    The final summary must be a specific length so that when it is read aloud at a pace of {wpm} words per minute, the total duration is exactly {duration_seconds} seconds.

    Based on this, the summary should be EXACTLY {target_word_count} words long. Please generate a concise and natural-sounding summary that fits these constraints.
    Do not add any extra text, titles, or introductions.

    TRANSCRIPT:
    ---
    {transcript}
    ---
    """

    try:
        print(f"Sending request to Ollama model '{model}'...")
        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        summary = response['message']['content'].strip()
        print(f"Ollama generated a summary of {len(summary.split())} words.")
        return summary
    except Exception as e:
        print(f"An error occurred while contacting Ollama: {e}")
        return None

def create_timed_audio(text, duration_seconds, filename="summary_audio.mp3"):
    # ... (keep this function unchanged)
    if not text: return
    try:
        actual_word_count = len(text.split())
        required_wpm = (actual_word_count * 60) / duration_seconds
        print("\n--- Audio Generation ---")
        print(f"Required audio speaking rate: {required_wpm:.2f} WPM")
        engine = pyttsx3.init()
        engine.setProperty('rate', required_wpm)
        engine.save_to_file(text, filename)
        engine.runAndWait()
        print(f"✅ Successfully created synchronized audio file: '{filename}'")
    except Exception as e:
        print(f"An error occurred during audio generation: {e}")

def create_sentence_transcript(text, duration_seconds):
    # ... (keep this function unchanged)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    if not sentences: return []
    words = text.split()
    if not words: return []
    time_per_word = duration_seconds / len(words)
    transcript = []
    current_time = 0.0
    for sentence in sentences:
        num_words_in_sentence = len(sentence.split())
        sentence_duration = num_words_in_sentence * time_per_word
        start_time = current_time
        end_time = current_time + sentence_duration
        transcript.append({'sentence': sentence, 'start': start_time, 'end': end_time})
        current_time = end_time
    return transcript

def format_srt_time(seconds):
    # ... (keep this function unchanged)
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"

def generate_srt_file(sentence_transcript, filename="summary_subtitle.srt"):
    # ... (keep this function unchanged)
    with open(filename, 'w', encoding='utf-8') as f:
        for i, line in enumerate(sentence_transcript, 1):
            start = format_srt_time(line['start'])
            end = format_srt_time(line['end'])
            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{line['sentence']}\n\n")
    print(f"✅ Successfully created subtitle file: '{filename}'")

def get_audio_duration(file_path):
    """Gets the duration of a media file in seconds using ffprobe."""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting duration for {file_path}: {e}")
        return None

def get_video_properties(file_path):
    """Gets video resolution (WxH) and duration using ffprobe."""
    # Check if file exists and is readable first
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return None, None
    
    if not os.access(file_path, os.R_OK):
        print(f"Error: Cannot read file (permission issue): {file_path}")
        return None, None
    
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-show_entries', 'format=duration',
        '-of', 'json',
        file_path
    ]
    
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               check=True, text=True, encoding='utf-8')
        data = json.loads(result.stdout)
        
        # Extract duration and resolution
        duration = float(data['format']['duration'])
        width = data['streams'][0]['width']
        height = data['streams'][0]['height']
        
        return f"{width}x{height}", duration
        
    except subprocess.CalledProcessError as e:
        print(f"FFprobe error (exit code {e.returncode}): {e.stderr}")
        return None, None
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"Error parsing FFprobe output: {e}")
        print(f"FFprobe output: {result.stdout if 'result' in locals() else 'N/A'}")
        return None, None

def get_duration_fallback(file_path):
    """Alternative method to get video duration"""
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              check=True, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Fallback duration check also failed: {e}")
        return None

def create_final_video_ffmpeg(video_path, audio_path, srt_path, output_path="final_video_ffmpeg.mp4"):
    """
    Combines video, audio, and subtitles using direct ffmpeg commands.
    """
    print("\n--- Final Video Creation (using FFmpeg) ---")

    # Verify all input files exist
    for path, name in [(video_path, "video"), (audio_path, "audio"), (srt_path, "subtitle")]:
        if not os.path.exists(path):
            print(f"❌ {name} file not found: {path}")
            return

    video_res, video_duration = get_video_properties(video_path)
    audio_duration = get_audio_duration(audio_path)

    if video_duration is None:
        print("❌ Could not determine video properties. Trying alternative approach...")
        # Try a different method to get video properties
        video_duration = get_duration_fallback(video_path)
        
    if video_duration is None or audio_duration is None:
        print("❌ Could not determine media properties. Aborting.")
        return

    # Escape the SRT path for the ffmpeg filter syntax
    escaped_srt_path = srt_path.replace('\\', '/').replace(':', '\\:')

    command = []
    if audio_duration > video_duration:
        print(f"Audio is longer ({audio_duration:.2f}s) than video ({video_duration:.2f}s). Extending video with black frames.")
        
        # This complex filter creates a black canvas, overlays the video, then adds subtitles
        filter_complex = (
            f"color=c=black:s={video_res}:d={audio_duration}[black];"
            f"[0:v]settb=AVTB[mainv];"
            f"[black][mainv]overlay=shortest=0[paddedv];"
            f"[paddedv]subtitles='{escaped_srt_path}'[outv]"
        )
        
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-y',
            output_path
        ]

    else:
        print(f"Video is longer ({video_duration:.2f}s) than audio ({audio_duration:.2f}s). Final output will match audio duration.")
        command = [
            'ffmpeg',
            '-i', video_path,
            '-i', audio_path,
            '-vf', f"subtitles='{escaped_srt_path}'",
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-map', '0:v',
            '-map', '1:a',
            '-t', str(audio_duration),
            '-y',
            output_path
        ]
    
    try:
        print(f"Executing FFmpeg command: {' '.join(shlex.quote(c) for c in command)}")
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Successfully created final video: '{output_path}'")
    except subprocess.CalledProcessError as e:
        print("❌ An error occurred during FFmpeg processing.")
        print(f"Stderr: {e.stderr.decode() if e.stderr else 'N/A'}")