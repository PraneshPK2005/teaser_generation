# -------------------------------
# Imports
# -------------------------------
import os
import json
import torch
import cv2
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector


# -------------------------------
# Scene Detection with PySceneDetect
# -------------------------------
def detect_scenes(video_path, threshold=12.0):
    """
    Detect scene change timestamps (in seconds) using PySceneDetect.
    """
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold))

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scene_list = scene_manager.get_scene_list()

    return [start.get_seconds() for start, _ in scene_list]


def extract_frames(video_path, timestamps, output_dir="frames"):
    """
    Extract frames from video at given timestamps.
    Returns a list of dicts: [{'timestamp': float, 'path': str}, ...]
    """
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise FileNotFoundError(f"Error: Could not open video file {video_path}")

    frames = []
    for i, ts in enumerate(timestamps):
        cap.set(cv2.CAP_PROP_POS_MSEC, ts * 1000)
        ret, frame = cap.read()
        if ret:
            frame_path = os.path.join(output_dir, f"frame_{i:04d}_{ts:.2f}.jpg")
            cv2.imwrite(frame_path, frame)
            frames.append({"timestamp": ts, "path": frame_path})

    cap.release()
    return frames


def fallback_frame_extraction(video_path, interval=5, output_dir="frames"):
    """
    Extract frames every N seconds as fallback when scene detection fails.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    cap.release()

    timestamps = [i for i in range(0, int(duration) + 1, interval)]
    return extract_frames(video_path, timestamps, output_dir)


# -------------------------------
# BLIP Caption Generation
# -------------------------------
def load_blip_model():
    """
    Load BLIP image captioning model (large version).
    """
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large", use_fast=True)
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return processor, model, device


def generate_visual_descriptions(processor, model, device, frames):
    """
    Generate visual captions for each frame.
    Returns a list of dicts: [{'timestamp': float, 'text': str}, ...]
    """
    descriptions = []
    for frame in frames:
        image = Image.open(frame["path"]).convert("RGB")
        inputs = processor(images=image, return_tensors="pt").to(device)
        output = model.generate(**inputs, max_new_tokens=50)
        caption = processor.decode(output[0], skip_special_tokens=True)
        descriptions.append({"timestamp": round(frame["timestamp"], 2), "text": caption})

    return descriptions


# -------------------------------
# Main Function
# -------------------------------
def process_video_for_visual_description(video_path, output_dir="frames"):
    """
    Main function to process video and return visual descriptions.
    """
    # Step 1: Detect scenes
    timestamps = detect_scenes(video_path, threshold=12.0)

    # Step 2: Extract frames (fallback if scene detection fails)
    frames = extract_frames(video_path, timestamps, output_dir) if timestamps else fallback_frame_extraction(video_path, output_dir=output_dir)

    # Step 3: Load BLIP model
    processor, model, device = load_blip_model()

    # Step 4: Generate raw visual descriptions
    descriptions = generate_visual_descriptions(processor, model, device, frames)

    # Step 5: Format descriptions as list of strings
    formatted_descriptions = [f"[{desc['timestamp']:.2f}s] {desc['text']}" for desc in descriptions]

    return formatted_descriptions



# -------------------------------
# Example usage (only for testing)
# -------------------------------
if __name__ == "__main__":
    video_file = r"P:\cts npn\practise\Terminator 2_ Judgment Day movie review.mp4"
    visual_descriptions = process_video_for_visual_description(video_file, output_dir="extracted_frames")
    print(visual_descriptions)

    with open("video_descriptions.json", "w") as f:
        json.dump(visual_descriptions, f, indent=4)

    print(f"Saved {len(visual_descriptions)} descriptions to video_descriptions.json")
