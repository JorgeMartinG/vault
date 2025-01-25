import aiofiles
import json
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List
from utils import get_video_info, format_size
from transcoding.queue import QueueManager
from transcoding.process import VideoProcessor
from transcoding.daemon import ProcessorDaemon
from contextlib import asynccontextmanager
from transcoding.logger import VideoLogger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application"""

    processor_daemon = ProcessorDaemon(
        queue_manager=queue_manager, 
        video_processor=video_processor,
        logger=logger,
        check_interval=config["processing"]["check_interval"]
    )
    processor_daemon.start()
    yield
    processor_daemon.stop()

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

with open("/var/www/vault/app/api/config/config.json") as config_file:
    config = json.load(config_file)

cors = config["cors"]
path = config["path"]
queue_manager = QueueManager(Path(path["queue"]), config)
logger = VideoLogger(Path(path["logs"]))

video_processor = VideoProcessor(
    input_dir=Path(path["uploads"]),
    output_dir=Path(path["processed"]),
    queue_manager=queue_manager,
    logger=logger
)

upload_dir = Path(path["uploads"]).resolve()
output_dir = Path(path["processed"]).resolve()
upload_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=cors["origin"],
    allow_methods=cors["method"],
    allow_headers=cors["header"],
    allow_credentials=True,
)

@app.post("/api/uploads/")
async def create_upload_file(file_uploads: List[UploadFile] = File(...)) -> list:
    """Handles uploading multiple files."""

    uploaded_files = []
    for file in file_uploads:
        save_to = upload_dir / file.filename
        try:
            async with aiofiles.open(save_to, "wb") as f:
                while contents := await file.read(4 * 1024 * 1024):
                    await f.write(contents)
            uploaded_files.append(file.filename)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error saving file {file.filename}: {e}")
        finally:
            await file.close()
    return uploaded_files

@app.get("/api/files/")
async def list_upload_file() -> dict:
    """Lists all files in the uploads directory."""

    try:
        files = []
        for filename in os.listdir(upload_dir):
            file_path = upload_dir / filename
            if file_path.is_file():
                file_info = {"filename": filename, "size": format_size(file_path.stat().st_size)}
            if filename.lower().endswith(('.mp4', '.mkv', '.ts')):
                file_info.update(get_video_info(file_path))
            files.append(file_info)
        
        if not files:
            return {"message": "No files found"}
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files in {upload_dir}: {e}")

@app.delete("/api/files/{filename}")
async def delete_file(filename: str) -> None:
    """Delete a specific file from the uploads directory."""

    file_path = upload_dir / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    try:
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file {filename}: {e}")

@app.post("/api/process/{filename}")
async def process_video(filename: str):
    """Add a video to the processing queue"""

    try:
        task_id = queue_manager.add_task(filename)
        return {
            "status": "success",
            "task_id": task_id,
            "message": "Video added to processing queue"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/process/status/{task_id}")
async def get_process_status(task_id: str) -> dict:
    """Get the status of a processing task."""
    
    queue_data = queue_manager._load_queue()
    current_status = queue_manager._find_task_status(task_id, queue_data)
    
    if not current_status:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task = queue_manager._get_task_status(task_id, current_status, queue_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task

# @app.get("/api/process/queue")
# async def get_queue_status():
#     """Get the status of all tasks in the queue"""
#     queue_data = queue_manager._load_queue()
#     return {
#         "pending": len(queue_data["pending"]),
#         "processing": len(queue_data["processing"]),
#         "completed": len(queue_data["completed"]),
#         "tasks": {
#             "pending": queue_data["pending"],
#             "processing": queue_data["processing"],
#             "completed": queue_data["completed"][-10:]  # Return only last 10 completed tasks
#         }
#     }

@app.get("/api/processed/")
async def list_processed_files() -> dict:
    """List all processed video files."""
    try:
        files = []
        for filename in os.listdir(output_dir):
            file_path = output_dir / filename
            if file_path.is_file():
                file_info = {
                    "filename": filename,
                    "size": format_size(file_path.stat().st_size)
                }
                if filename.lower().endswith(('.mp4', '.mkv', '.ts')):
                    file_info.update(get_video_info(file_path))
                files.append(file_info)
        
        if not files:
            return {"message": "No processed files found"}
        return {"files": files}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing processed files: {e}"
        )

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        log_level="debug",
        timeout_keep_alive=60,
        reload=False,
    )