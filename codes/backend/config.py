# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FFmpeg configuration
FFMPEG_PATH = r'C:/Users/Pranesh/Downloads/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin'
os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ['PATH']

# AWS configuration
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

# Model configuration
WHISPER_MODEL = "small"
BLIP_MODEL = "Salesforce/blip-image-captioning-large"
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'

# Path configuration
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
OUTPUT_DIR = BASE_DIR / "output"
FRAMES_DIR = OUTPUT_DIR / "frames"

# Create directories
DOWNLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
FRAMES_DIR.mkdir(exist_ok=True)