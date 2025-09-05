import subprocess
from pathlib import Path
from fastapi import HTTPException
from app.utils.file_manager import scan_file, update_job_status


def process_job(input_path: Path, output_path: Path, job_id: str):
    """
    Run antivirus scan and FFmpeg in sequence.
    """
    try:
        # Scan file
        scan_file(input_path)

        # Run FFmpeg
        command = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            str(output_path),
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        update_job_status(job_id, "done")

    except subprocess.CalledProcessError as e:
        update_job_status(job_id, "failed", "ffmpeg conversion error.")
        print(f"[ERROR] FFmpeg failed for job {job_id}: {e.stderr.decode() if e.stderr else e}")

    except HTTPException as e:
        update_job_status(job_id, "failed", e.detail)    

    except Exception as e:
        update_job_status(job_id, "failed", str(e))
        print(f"[ERROR] Unexpected error for job {job_id}: {e}")
