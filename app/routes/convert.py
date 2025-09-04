from fastapi import APIRouter, Form, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.utils.file_manager import (
    generate_job_id,
    save_upload_file,
    prepare_output_path,
    register_job,
    get_job,
    cleanup_job_files,
)
from app.services.converter import run_ffmpeg

router = APIRouter(prefix="/convert", tags=["convert"])


@router.post("/")
def convert_file(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    output_format: str = Form(...),
):
    """
    Start a new conversion job.
    """
    try:
        job_id = generate_job_id()

        # Save input file
        input_path = save_upload_file(file, job_id)
        output_path = prepare_output_path(job_id, output_format)

        # Register job
        register_job(job_id, input_path, output_path)

        # Run FFmpeg in background
        background_tasks.add_task(run_ffmpeg, input_path, output_path, job_id)

        return {"job_id": job_id, "status": "processing"}
    except Exception as e:
        print(f"[ERROR] {e}")
        raise


@router.get("/status/{job_id}")
def check_status(job_id: str):
    """
    Check the status of a conversion job.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"job_id": job_id, "status": job["status"]}


@router.get("/download/{job_id}")
def download_file(job_id: str):
    """
    Download the converted file if job is done.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] != "done":
        raise HTTPException(status_code=400, detail="Job not finished yet")

    output_path = job["output"]

    if not output_path:
        raise HTTPException(status_code=500, detail="Output file missing")

    # Return the converted file
    response = FileResponse(
        path=output_path,
        filename=f"{job_id}{output_path.split('.')[-1]}",
        media_type="application/octet-stream"
    )

    return response
