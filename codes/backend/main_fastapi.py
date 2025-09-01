from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import tempfile
import shutil
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, EmailStr
import bcrypt
import uuid
import json
from datetime import datetime, timedelta
from db import users_collection, user_history_collection
from db_helper import save_teaser_history
from config import FFMPEG_PATH
import re

# Import your existing function
from main import process_video_to_teaser

# Set FFmpeg path for the entire application
os.environ['PATH'] = FFMPEG_PATH + os.pathsep + os.environ['PATH']

# Session storage (in production, use Redis or database)
sessions = {}

# Security
security = HTTPBearer()

class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SessionData(BaseModel):
    email: str
    username: str

app = FastAPI(title="Video Teaser Generator API")

# Configure CORS to allow frontend connections
origins = [

    "http://localhost:3000",

    "http://127.0.0.1:3000",

    "http://localhost:5173",

    "http://127.0.0.1:5173",

    "http://internally-dear-jaybird.ngrok-free.app",

    "https://teaser-generation.vercel.app"

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Received {request.method} request for {request.url}")
    print(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    print(f"Response status: {response.status_code}")
    return response

# Helper function to create session
def create_session(email: str, username: str) -> str:
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "email": email,
        "username": username,
        "expires": datetime.now() + timedelta(hours=24)
    }
    return session_id

# Helper function to validate session
def get_session(session_id: str) -> Optional[SessionData]:
    if session_id not in sessions:
        return None
    
    session = sessions[session_id]
    if session["expires"] < datetime.now():
        del sessions[session_id]
        return None
    
    return SessionData(**session)

# Dependency to get current user from session
async def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_data = get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return session_data

def create_temp_directory():
    """
    Create a temporary directory with proper permissions
    """
    try:
        # Try using system temp directory first
        temp_dir = tempfile.mkdtemp(prefix="teaser_")
        print(f"Created temp directory: {temp_dir}")
        return temp_dir
    except Exception as e:
        print(f"Failed to create system temp dir: {e}")
        
        # Fallback: try current working directory
        try:
            fallback_dir = os.path.join(os.getcwd(), "temp_uploads", str(uuid.uuid4()))
            os.makedirs(fallback_dir, exist_ok=True)
            print(f"Created fallback temp directory: {fallback_dir}")
            return fallback_dir
        except Exception as e2:
            print(f"Failed to create fallback temp dir: {e2}")
            raise HTTPException(
                status_code=500, 
                detail=f"Cannot create temporary directory: {str(e2)}"
            )

def safe_cleanup_directory(directory_path: str):
    """
    Safely clean up temporary directory
    """
    try:
        if os.path.exists(directory_path):
            # On Windows, sometimes files are still in use, so we retry
            import time
            for attempt in range(3):
                try:
                    shutil.rmtree(directory_path)
                    print(f"Cleaned up temp directory: {directory_path}")
                    break
                except (PermissionError, OSError) as e:
                    if attempt == 2:  # Last attempt
                        print(f"Warning: Could not clean up temp directory {directory_path}: {e}")
                    else:
                        time.sleep(0.5)  # Wait before retry
    except Exception as e:
        print(f"Warning: Error during cleanup: {e}")

@app.get("/health")
async def health_check():
    print("Health check endpoint called")
    return {"status": "healthy"}

@app.post("/signup")
async def signup(user: UserSignup):
    # Check if email already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    
    # Insert user into MongoDB
    users_collection.insert_one({
        "username": user.username,
        "email": user.email,
        "password": hashed_pw.decode("utf-8"),
    })

    return {"message": "User registered successfully"}

@app.post("/login")
async def login(response: Response, user: UserLogin):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user or not bcrypt.checkpw(user.password.encode(), db_user["password"].encode()):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Create session
    session_id = create_session(db_user["email"], db_user["username"])

    # Set cookie WITHOUT domain
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=24*60*60,
        samesite="none",  # or "strict"
        secure=True       # True if using HTTPS
    )

    return {
        "message": "Login successful",
        "username": db_user["username"],
        "email": db_user["email"]
    }

@app.post("/logout")
async def logout(response: Response, current_user: SessionData = Depends(get_current_user)):
    # Remove session
    session_id = None
    for sid, data in sessions.items():
        if data["email"] == current_user.email:
            session_id = sid
            break
    
    if session_id:
        del sessions[session_id]
    
    # Clear session cookie
    response.delete_cookie("session_id")
    
    return {"message": "Logout successful"}

@app.get("/profile")
async def get_history(current_user: SessionData = Depends(get_current_user)):
    """
    Get user's teaser history by email from session
    """
    # Find the user's history document
    history_doc = user_history_collection.find_one({"email": current_user.email})
    
    if not history_doc:
        return []
    
    # Return the teasers array
    return history_doc.get("teasers", [])

@app.post("/generate-teaser")
async def generate_teaser(
    request: Request,
    method: str = Form(...),
    max_length: int = Form(70),
    min_length: int = Form(60),
    youtube_url: Optional[str] = Form(None),
    video_file: Optional[UploadFile] = File(None),
    current_user: SessionData = Depends(get_current_user)
):
    """
    Generate a teaser video from either YouTube URL or uploaded file
    """
    if not youtube_url and not video_file:
        raise HTTPException(status_code=400, detail="Either YouTube URL or video file must be provided")
    if youtube_url and video_file:
        raise HTTPException(status_code=400, detail="Provide either YouTube URL or video file, not both")
    
    valid_methods = ["learning_a", "learning_b", "cinematic_a", "gemini"]
    if method not in valid_methods:
        raise HTTPException(status_code=400, detail=f"Method must be one of: {', '.join(valid_methods)}")

    # Create temporary directory with proper permissions
    temp_dir = create_temp_directory()
    
    try:
        if youtube_url:
            print(f"Processing YouTube URL: {youtube_url}")
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
            print(f"Processing uploaded file: {video_file.filename}")
            
            # Sanitize filename for Windows and create safe path
            safe_filename = re.sub(r'[\\/*?:"<>|]', "_", video_file.filename)
            # Add timestamp to make filename unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(safe_filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            file_path = os.path.join(temp_dir, unique_filename)
            
            print(f"Saving file to: {file_path}")
            
            # Save uploaded file with better error handling
            try:
                with open(file_path, "wb") as buffer:
                    # Read file in chunks to avoid memory issues
                    while chunk := await video_file.read(8192):  # 8KB chunks
                        buffer.write(chunk)
                print(f"File saved successfully: {file_path}")
            except Exception as file_error:
                print(f"Error saving file: {file_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Failed to save uploaded file: {str(file_error)}"
                )

            # Verify file was saved
            if not os.path.exists(file_path):
                raise HTTPException(
                    status_code=500, 
                    detail="File was not saved properly"
                )
            
            print(f"File size: {os.path.getsize(file_path)} bytes")

            # Process uploaded file
            result = process_video_to_teaser(
                input_source=file_path,
                max_length=max_length,
                min_length=min_length,
                is_youtube=False,
                method=method,
                output_dir=temp_dir
            )

        # Save teaser history
        save_teaser_history(
            user_email=current_user.email,
            method=method,
            youtube_url=youtube_url if youtube_url else None,
            main_file_url=result.get("video_s3_url"),
            teaser_file_url=result.get("s3_url"),
            duration=result.get("duration"),
            extra_data={
                "summary_text": result.get("summary"),
                "timestamps_used": result.get("timestamps")
            }
        )

        return JSONResponse(content=result)

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except PermissionError as pe:
        print(f"Permission error details: {pe}")
        raise HTTPException(
            status_code=500, 
            detail=f"File permission error. Please check if the application has write permissions to the temporary directory."
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing video: {str(e)}")
    finally:
        # Clean up temporary directory
        safe_cleanup_directory(temp_dir)

@app.get("/me")
async def get_current_user_info(current_user: SessionData = Depends(get_current_user)):
    """
    Get current user information
    """
    return {
        "email": current_user.email,
        "username": current_user.username
    }

@app.get("/")
async def root():
    return {"message": "Video Teaser Generator API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)