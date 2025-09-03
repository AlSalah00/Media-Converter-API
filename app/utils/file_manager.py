import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
import shutil
import magic  
import clamd  

from app.config import UPLOAD_DIR, OUTPUT_DIR, JOBS

clamd_client = clamd.ClamdUnixSocket()

def generate_job_id() -> str:
    """Generate a unique job ID (UUID)."""
    return str(uuid.uuid4())

def validate_file(upload_file: UploadFile):
    """Triple-check file: extension, header, and magic must all match allowed types."""

    # --- Extension check ---
    ext = Path(upload_file.filename).suffix.lower().lstrip(".")
    ext_to_mime = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "svg": "image/svg+xml",
        "webp": "image/webp",
        "mkv": "video/x-matroska",
        "mp4": "video/mp4",
        "wmv": "video/x-ms-wmv",
        "avi": "video/x-msvideo",
        "mp3": "audio/mpeg",
        "flac": "audio/flac",
        "aiff": "audio/x-aiff",
        "aac": "audio/aac",
        "wav": "audio/wav",
    }

    expected_mime = ext_to_mime.get(ext)
    if not expected_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: .{ext}",
        )

    # --- Header check ---
    if upload_file.content_type != expected_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mismatch between extension and header type: "
                   f".{ext} expected {expected_mime}, got {upload_file.content_type}",
        )

    # --- Magic check ---
    sample_bytes = upload_file.file.read(2048)  # read a chunk
    upload_file.file.seek(0)  # reset pointer
    mime = magic.Magic(mime=True)
    detected_type = mime.from_buffer(sample_bytes)

    if detected_type != expected_mime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mismatch between extension/header and actual file type: "
                   f".{ext} expected {expected_mime}, got {detected_type}",
        )

def scan_file(path: Path):
    """Scan file using ClamAV before conversion."""
    try:
        result = clamd_client.scan(str(path))
        if result and any("FOUND" in r for r in result.values()):
            path.unlink(missing_ok=True)  # delete infected file
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File rejected: contains malware",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Antivirus scan failed: {e}",
        )

def save_upload_file(upload_file: UploadFile, job_id: str) -> Path:
    """
    Save the uploaded file after validation + AV scan.
    """
    validate_file(upload_file)

    file_extension = Path(upload_file.filename).suffix
    input_path = UPLOAD_DIR / f"{job_id}{file_extension}"

    with input_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    # Scan with ClamAV
    scan_file(input_path)

    return input_path

def prepare_output_path(job_id: str, output_format: str) -> Path:
    return OUTPUT_DIR / f"{job_id}.{output_format}"

def register_job(job_id: str, input_path: Path, output_path: Path):
    JOBS[job_id] = {
        "status": "processing",
        "input": str(input_path),
        "output": str(output_path),
    }

def update_job_status(job_id: str, status: str):
    if job_id in JOBS:
        JOBS[job_id]["status"] = status

def get_job(job_id: str) -> dict | None:
    return JOBS.get(job_id)

def cleanup_job_files(job_id: str):
    job = JOBS.pop(job_id, None)
    if job:
        for path in [job.get("input"), job.get("output")]:
            if path and Path(path).exists():
                Path(path).unlink(missing_ok=True)