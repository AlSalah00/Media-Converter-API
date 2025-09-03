import subprocess
from pathlib import Path
from app.utils.file_manager import update_job_status


def run_ffmpeg(input_path: Path, output_path: Path, job_id: str):
    """
    Convert media using FFmpeg.
    """
    try:
        command = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            str(output_path),
        ]

        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        update_job_status(job_id, "done")

    except subprocess.CalledProcessError as e:
        update_job_status(job_id, "failed")
        print(f"[ERROR] FFmpeg failed for job {job_id}: {e.stderr.decode() if e.stderr else e}")

    except Exception as e:
        update_job_status(job_id, "failed")
        print(f"[ERROR] Unexpected error for job {job_id}: {e}")
