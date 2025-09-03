import os
from pathlib import Path

# API SETTINGS
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable is not set!")

# PATH SETTINGS
# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory to store uploaded and converted files
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# JOB SETTINGS
JOBS: dict[str, dict] = {}

# Allowed formats (expand as needed)
ALLOWED_INPUT_FORMATS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "mp4", "mkv", "wmv", "avi", "mp3", "wav", "flac", "aiff", "aac"}
ALLOWED_OUTPUT_FORMATS = {"png", "jpg", "jpeg", "gif", "svg", "webp", "mp4", "mkv", "wmv", "avi", "mp3", "wav", "flac", "aiff", "aac"}