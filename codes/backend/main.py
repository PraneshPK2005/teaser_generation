# main.py
import os
import json
from pathlib import Path
from datetime import datetime

# Import centralized configuration
from config import OUTPUT_DIR, FRAMES_DIR

# Import your custom modules
from get_videos_from_url import handle_video_input, upload_file_to_s3
from transcribe_audio_from_whisper import transcribe_audio
from get_description_from_blip import process_video_for_visual_description
from clean_audio_transcripts import preprocess_audio
from clean_visual_descriptions import preprocess_visual
from create_embeddings_and_query import teaser_pipeline
from get_timestamps_from_embeds_output import extract_timestamps_by_method
# Updated import to include new functions
from ollama_summarization_voiceover import (
    summarize_text,
    create_timed_audio,
    create_sentence_transcript,
    generate_srt_file,
    create_final_video_ffmpeg
)
from making_teaser_from_timestamps import crop_and_merge_clips_ffmpeg
from gemini_for_timestamps import generate_timestamps_with_gemini

def process_video_to_teaser(input_source, max_length=70, min_length=60, is_youtube=True, method="learning_b", output_dir=OUTPUT_DIR):
    """
    Main workflow to generate a teaser from either YouTube URL or uploaded video
    """
    Path(output_dir).mkdir(exist_ok=True)

    print("Step 1: Processing video input...")
    video_path, audio_path, video_s3_url, audio_s3_url, base_filename = handle_video_input(
        input_source, is_youtube=is_youtube
    )

    audio_path = str(Path(audio_path).resolve())
    video_path = str(Path(video_path).resolve())

    print(f"Audio path: {audio_path}")
    print(f"Video path: {video_path}")

    # Verify files exist before proceeding
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if method == "gemini":
        print("Step 2: Generating timestamps with Gemini...")
        timestamps, total_duration = generate_timestamps_with_gemini(video_path, max_length, min_length)
        with open(os.path.join(output_dir, "timestamps.json"), "w") as f:
            json.dump(timestamps, f, indent=2)

        print(f"Total teaser duration: {total_duration:.2f} seconds")
        print("Step 8: Creating final teaser...")
        teaser_output = os.path.join(output_dir, "teaser_output.mp4")

        local_teaser_path = crop_and_merge_clips_ffmpeg(
            video_path=video_path,
            timestamps=timestamps,
            output_path=teaser_output,
            method=method,
            external_audio_path=None
        )

    else:
        print("Step 2: Transcribing audio...")
        raw_audio_transcripts = transcribe_audio(audio_path)

        print("Step 3: Generating visual descriptions...")
        raw_visual_descriptions = process_video_for_visual_description(video_path, output_dir=FRAMES_DIR)

        print("Step 4: Cleaning transcripts and descriptions...")
        cleaned_audio = preprocess_audio(raw_audio_transcripts)
        cleaned_visual = preprocess_visual(raw_visual_descriptions)

        with open(os.path.join(output_dir, "cleaned_audio.json"), "w") as f:
            json.dump(cleaned_audio, f, indent=2)
        with open(os.path.join(output_dir, "cleaned_visual.json"), "w") as f:
            json.dump(cleaned_visual, f, indent=2)

        print("Step 5: Creating embeddings and querying for best segments...")
        if method == "learning_a":
            audio_query = "Extract the most impactful and meaningful speech segments from the audio transcript that can create a strong teaser. Prioritize moments of high engagement, including welcoming introductions and send-off or closing remarks."
            visual_query = ""
        elif method == "learning_b":
            audio_query = "key points and summary"
            visual_query = "Identify the most visually striking and dramatic scenes suitable for a teaser. Focus on visually engaging and attention-grabbing moments that are cinematic and memorable."
        elif method == "cinematic_a":
            audio_query = "Key points and summary for teaser."
            visual_query = "Identify the most visually striking and dramatic scenes suitable for a teaser. Focus on visually engaging and attention-grabbing moments that are cinematic and memorable."

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
        timestamps = extract_timestamps_by_method(method, audio_results, visual_results)

        with open(os.path.join(output_dir, "timestamps.json"), "w") as f:
            json.dump(timestamps, f, indent=2)

        print(f"Total teaser duration: {total_duration:.2f} seconds")

        voiceover_path = None
        summary_text = None
        srt_path = None
        if method in ["learning_b", "cinematic_a"]:
            print("Step 7: Generating voiceover summary...")
            full_transcript = " ".join([item['text'] for item in cleaned_audio])

            summary_text = summarize_text(
                transcript=full_transcript,
                duration_seconds=total_duration,
                wpm=140
            )

            if summary_text:
                voiceover_path = os.path.join(output_dir, "voiceover.mp3")
                create_timed_audio(
                    text=summary_text,
                    duration_seconds=total_duration,
                    filename=voiceover_path
                )

                # Generate sentence-level transcript and subtitles
                print("Step 7.1: Creating subtitle file...")
                sentence_transcript = create_sentence_transcript(summary_text, total_duration)
                srt_path = os.path.join(output_dir, "voiceover_subtitles.srt")
                generate_srt_file(sentence_transcript, srt_path)
            else:
                print("Warning: Voiceover generation failed, proceeding without voiceover")

        print("Step 8: Creating final teaser...")
        teaser_output = os.path.join(output_dir, "teaser_output.mp4")

        # If voiceover exists, merge with video + subtitles using FFmpeg
        if voiceover_path and srt_path and os.path.exists(voiceover_path) and os.path.exists(srt_path):
            try:
                create_final_video_ffmpeg(
                    video_path=video_path,
                    audio_path=voiceover_path,
                    srt_path=srt_path,
                    output_path=teaser_output
                )
                local_teaser_path = teaser_output
            except Exception as e:
                print(f"Error creating final video with FFmpeg: {e}")
                print("Falling back to basic clip merging...")
                local_teaser_path = crop_and_merge_clips_ffmpeg(
                    video_path=video_path,
                    timestamps=timestamps,
                    output_path=teaser_output,
                    method=method,
                    external_audio_path=voiceover_path
                )
        else:
            # No voiceover, fallback to teaser clip merge
            local_teaser_path = crop_and_merge_clips_ffmpeg(
                video_path=video_path,
                timestamps=timestamps,
                output_path=teaser_output,
                method=method,
                external_audio_path=voiceover_path
            )

    print("Step 9: Uploading final teaser to S3...")
    teaser_s3_key = f"teasers/{base_filename}_teaser.mp4"
    teaser_s3_url = upload_file_to_s3(local_teaser_path, teaser_s3_key)

    print(f"Teaser generation complete! Download at: {teaser_s3_url}")

    return {
        "s3_url": teaser_s3_url,
        "local_path": local_teaser_path,
        "timestamps": timestamps,
        "duration": total_duration,
        "video_s3_url": video_s3_url,
        "audio_s3_url": audio_s3_url,
        "summary": summary_text if method == "learning_b" else None,
        "method": method,
        "status": "success"
    }

# Example run
if __name__ == "__main__":
    input_source = r"C:\Users\Pranesh\Downloads\Earth_s_Evolution_in_10_Minutes.mp4"
    process_video_to_teaser(input_source, max_length=70, min_length=60, is_youtube=False, method="gemini", output_dir=OUTPUT_DIR)