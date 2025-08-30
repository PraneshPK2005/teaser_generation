# main_fastapi.py
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional

# Import centralized configuration
from config import FFMPEG_PATH

# Set FFmpeg path for the entire application
os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ['PATH']

# Import your existing function
from main import process_video_to_teaser

app = FastAPI(title="Video Teaser Generator API")

# Configure CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",        # React Vite default
        "http://127.0.0.1:3000",        # Alternative localhost
        "http://localhost:5173",        # Vite's alternative port
        "http://127.0.0.1:5173"         # Vite's alternative port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Received {request.method} request for {request.url}")
    print(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    print(f"Response status: {response.status_code}")
    return response

@app.get("/health")
async def health_check():
    print("Health check endpoint called")
    return {"status": "healthy"}

@app.post("/generate-teaser")
async def generate_teaser(
    method: str = Form(...),
    max_length: int = Form(70),
    min_length: int = Form(60),
    youtube_url: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
):
    """
    Generate a teaser video from either YouTube URL or uploaded file
    """
    # Validate input
    if not youtube_url and not video_file:
        raise HTTPException(
            status_code=400, 
            detail="Either YouTube URL or video file must be provided"
        )
    
    if youtube_url and video_file:
        raise HTTPException(
            status_code=400, 
            detail="Provide either YouTube URL or video file, not both"
        )
    
    # Validate method
    valid_methods = ["learning_a", "learning_b", "cinematic_a", "gemini"]
    if method not in valid_methods:
        raise HTTPException(
            status_code=400, 
            detail=f"Method must be one of: {', '.join(valid_methods)}"
        )
    
    # Create a temporary directory for processing
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            if youtube_url:
                # Process YouTube URL
                result = process_video_to_teaser(
                    input_source=youtube_url,
                    max_length=max_length,
                    min_length=min_length,
                    is_youtube=True,
                    method=method,
                    output_dir=temp_dir
                )
            else:
                # Save uploaded file to temporary location
                file_path = os.path.join(temp_dir, video_file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(video_file.file, buffer)
                
                # Process uploaded file
                result = process_video_to_teaser(
                    input_source=file_path,
                    max_length=max_length,
                    min_length=min_length,
                    is_youtube=False,
                    method=method,
                    output_dir=temp_dir
                )
            
            # Return the result
            return JSONResponse(content=result)
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing video: {str(e)}"
            )

@app.get("/")
async def root():
    return {"message": "Video Teaser Generator API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)