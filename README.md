# Video Teaser Generator

A comprehensive pipeline for automatically generating engaging video teasers from YouTube videos or local files. This system uses AI to identify the most impactful moments and creates teasers within specified duration constraints.

## Features

- **YouTube Video Download**: Download videos and extract optimized audio for transcription
- **AI-Powered Transcription**: Convert audio to timestamped transcripts using Whisper
- **Smart Segment Selection**: Use Ollama AI models to identify the most engaging moments
- **Precise Duration Control**: Ensure teasers fit within specified time constraints (45-65 seconds by default)
- **Automated Video Editing**: Extract and combine selected segments into a final teaser
- **Cloud Integration**: Automatically upload assets to AWS S3 for storage and distribution

## Architecture

```
YouTube URL/Local File → Download/Extract → Transcribe → AI Analysis → Video Editing → Teaser Output
```

## Installation

### Prerequisites

- Python 3.8+
- FFmpeg
- AWS Account (for S3 storage)
- Ollama (for AI analysis)

### Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd video-teaser-generator
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install Ollama and required models:
```bash
# Install Ollama (visit https://ollama.ai for platform-specific instructions)
ollama pull llama3.2:3b
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your AWS credentials and configuration
```

### Environment Variables

Create a `.env` file with the following variables:

```env
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=us-east-1
BUCKET_NAME=your_s3_bucket_name
FFMPEG_PATH=C:/path/to/ffmpeg/bin  # Optional, for Windows
```

## Usage

### Basic Usage

Run the main orchestration script:

```bash
python main.py
```

This will process the default YouTube video and generate a teaser.

### Custom Usage

```python
from main import TeaserGenerator

# Initialize the generator
generator = TeaserGenerator()

# Process a YouTube video
result = generator.process_youtube_video(
    youtube_url="https://youtube.com/your-video",
    expected_time=45,  # Minimum duration in seconds
    max_sec=65         # Maximum duration in seconds
)

# Process a local video file
result = generator.process_local_video(
    video_path="path/to/your/video.mp4",
    expected_time=45,
    max_sec=65
)
```

### Individual Components

You can also use the individual components separately:

1. **Download videos from YouTube**:
```python
from get_videos_from_url import download_youtube_video_and_audio

video_path, audio_path = download_youtube_video_and_audio(
    "https://youtube.com/your-video",
    "downloads"
)
```

2. **Transcribe audio**:
```python
from transcribe_audio_from_whisper import transcribe_audio

transcription = transcribe_audio("path/to/audio.wav")
```

3. **Generate teaser timestamps**:
```python
from based_on_orig_transcripts import get_teaser_timestamps

timestamps = get_teaser_timestamps(transcription, 45, 65)
```

4. **Create teaser video**:
```python
from making_teaser_from_timestamps import crop_and_merge_clips_ffmpeg

result = crop_and_merge_clips_ffmpeg(
    video_path="path/to/video.mp4",
    timestamps=timestamps,
    output_path="teaser_output.mp4"
)
```

## File Structure

```
video-teaser-generator/
├── main.py                 # Main orchestration script
├── get_videos_from_url.py  # YouTube video downloader
├── transcribe_audio_from_whisper.py  # Audio transcription
├── based_on_orig_transcripts.py      # AI segment selection
├── making_teaser_from_timestamps.py  # Video editing
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── downloads/             # Downloaded videos and audio
├── outputs/               # Generated teasers
└── README.md             # This file
```

## Configuration

### AI Model Selection

The system uses Ollama's AI models for segment selection. You can modify the model in `based_on_orig_transcripts.py`:

```python
# Change this line to use a different model
response = client.generate(model='llama3.2:3b', prompt=prompt)
```

Available models include:
- `llama3.2:3b` (default)
- `llama3:8b`
- `mistral:7b`
- `gemma:7b`

### Duration Constraints

Adjust the teaser duration by modifying the `expected_time` and `max_sec` parameters:

```python
# For shorter teasers (30-45 seconds)
timestamps = get_teaser_timestamps(transcription, 30, 45)

# For longer teasers (60-90 seconds)  
timestamps = get_teaser_timestamps(transcription, 60, 90)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for audio transcription
- [Ollama](https://ollama.ai) for AI model inference
- [FFmpeg](https://ffmpeg.org) for video processing
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video downloading

## Support

For support or questions, please open an issue on GitHub or contact the development team.
