# main.py
import os
import json
from pathlib import Path
from datetime import datetime

# Import centralized configuration
from config import OUTPUT_DIR, FRAMES_DIR

# Import your custom modules
from get_videos_from_url import handle_video_input, upload_teaser_to_s3
from transcribe_audio_from_whisper import transcribe_audio
from get_description_from_blip import process_video_for_visual_description
from clean_audio_transcripts import preprocess_audio
from clean_visual_descriptions import preprocess_visual
from create_embeddings_and_query import teaser_pipeline
from get_timestamps_from_embeds_output import extract_timestamps_by_method
from ollama_summarization_voiceover import summarize_text, create_timed_audio
from making_teaser_from_timestamps import crop_and_merge_clips_ffmpeg

def process_video_to_teaser(input_source, max_length=70, min_length=60, is_youtube=True, method="learning_b", output_dir=OUTPUT_DIR):
    """
    Main workflow to generate a teaser from either YouTube URL or uploaded video
    """
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    print("Step 1: Processing video input...")
    # Process video input (YouTube URL or uploaded file)
    video_path, audio_path, video_s3_url, audio_s3_url = handle_video_input(
        input_source, is_youtube=is_youtube
    )
    
    # Ensure paths are absolute
    audio_path = str(Path(audio_path).resolve())
    video_path = str(Path(video_path).resolve())
    
    print(f"Audio path: {audio_path}")
    print(f"Video path: {video_path}")
    
    print("Step 2: Transcribing audio...")
    # Transcribe audio
    raw_audio_transcripts = transcribe_audio(audio_path)
    
    print("Step 3: Generating visual descriptions...")
    # Generate visual descriptions
    raw_visual_descriptions = process_video_for_visual_description(video_path, output_dir=FRAMES_DIR)
    
    print("Step 4: Cleaning transcripts and descriptions...")
    # Clean both audio and visual data
    cleaned_audio = preprocess_audio(raw_audio_transcripts)
    cleaned_visual = preprocess_visual(raw_visual_descriptions)
    
    # Save cleaned data for reference
    with open(os.path.join(output_dir, "cleaned_audio.json"), "w") as f:
        json.dump(cleaned_audio, f, indent=2)
    with open(os.path.join(output_dir, "cleaned_visual.json"), "w") as f:
        json.dump(cleaned_visual, f, indent=2)
    
    print("Step 5: Creating embeddings and querying for best segments...")
    # Define queries based on method
    if method == "learning_a":
        audio_query = "most engaging and informative dialogue"
        visual_query = ""  # Not used
    elif method == "learning_b":
        audio_query = "key points and summary"
        visual_query = "most relevant and descriptive visuals"
    elif method == "cinematic_a":
        audio_query = "cinematic and dramatic audio"
        visual_query = "most cinematic and visually appealing scenes"
    
    # Get results from embedding pipeline
    audio_results, visual_results, total_duration = teaser_pipeline(
        method, 
        max_length=max_length,
        min_length=min_length,
        audio_data=cleaned_audio, 
        visual_data=cleaned_visual,
        query_audio_text=audio_query,
        query_visual_text=visual_query
    )
    
    print("Step 6: Extracting timestamps...")
    # Extract timestamps based on method
    timestamps = extract_timestamps_by_method(method, audio_results, visual_results)
    
    # Save timestamps for reference
    with open(os.path.join(output_dir, "timestamps.json"), "w") as f:
        json.dump(timestamps, f, indent=2)
    
    print(f"Total teaser duration: {total_duration:.2f} seconds")
    
    # Handle voiceover generation for Learning Method B
    voiceover_path = None
    if method == "learning_b":
        print("Step 7: Generating voiceover summary...")
        # Combine all audio text for summarization
        full_transcript = " ".join([item['text'] for item in cleaned_audio])
        
        # Generate summary
        summary_text = summarize_text(
            transcript=full_transcript,
            duration_seconds=total_duration,
            wpm=140  # Words per minute
        )
        
        # Generate timed audio
        voiceover_path = os.path.join(output_dir, "voiceover.mp3")
        create_timed_audio(
            text=summary_text,
            duration_seconds=total_duration,
            filename=voiceover_path
        )
    
    print("Step 8: Creating final teaser...")
    # Create final teaser video
    teaser_output = os.path.join(output_dir, "teaser_output.mp4")
    
    result = crop_and_merge_clips_ffmpeg(
        video_path=video_path,
        timestamps=timestamps,
        output_path=teaser_output,
        method=method,
        external_audio_path=voiceover_path
    )
    
    print("Step 9: Uploading final teaser to S3...")
    # Upload teaser using the new function
    final_teaser_url = upload_teaser_to_s3(teaser_output)

    print(f"Teaser generation complete! Download at: {final_teaser_url}")

    return {
        "s3_url": final_teaser_url,
        "local_path": teaser_output,
        "timestamps": timestamps,
        "duration": total_duration,
        "video_s3_url": video_s3_url,
        "audio_s3_url": audio_s3_url,
        "method": method,
        "status": "success"
    }

if __name__ == "__main__":
    # Example usage with YouTube URL
    youtube_url = "https://www.youtube.com/watch?app=desktop&v=teOwJWveEkE"
    print("start time", datetime.now().strftime("%H:%M:%S"))
    result = process_video_to_teaser(youtube_url, is_youtube=True, method="cinematic_a")
    print(f"YouTube teaser created: {result}")
    print("end time", datetime.now().strftime("%H:%M:%S"))