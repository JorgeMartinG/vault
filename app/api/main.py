import aiofiles
import json
import os
from dataclasses import dataclass
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List
from utils import get_video_info, format_size
from core.process import VideoProcessor
from core.validate import FileValidator
from core.manager import QueueManager
from core.daemon import ProcessorDaemon
from core.logging import VideoLogger
from contextlib import asynccontextmanager

with open("/var/www/vault/app/api/config/config.json") as config_file:
    config = json.load(config_file)

file_validator = FileValidator(config["path"])
queue_manager = QueueManager(Path(config["path"]["queue"]), config)
logger = VideoLogger(Path(config["path"]["logs"]))

video_processor = VideoProcessor(
    input_dir=Path(config["path"]["uploads"]),
    output_dir=Path(config["path"]["processed"]),
    queue_manager=queue_manager,
    file_validator=file_validator,
    logger=logger
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    "Lifecycle manager for the FastAPI application"

    processor_daemon = ProcessorDaemon(
        queue_manager=queue_manager,
        video_processor=video_processor,
        logger=logger,
        file_validator=FileValidator,
        check_interval=config["processing"]["check_interval"]
    )

    processor_daemon.start()
    yield
    processor_daemon.stop()

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

upload_dir = Path(config["path"]["uploads"]).resolve()
output_dir = Path(config["path"]["processed"]).resolve()
upload_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=config["cors"]["origin"],
    allow_methods=config["cors"]["method"],
    allow_headers=config["cors"]["header"],
    allow_credentials=True,
)

@app.post("/api/uploads/")
async def create_upload_file(file_uploads: List[UploadFile] = File(...)) -> list:
    "Handles uploading multiple files."

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
    "Lists all files in the uploads directory."

    try:
        files = []
        for filename in os.listdir(upload_dir):
            file_path = upload_dir / filename
            if file_path.is_file():
                file_info = {"filename": filename, "size": format_size(file_path.stat().st_size)}
            if file_validator.validate_extension(filename):
                file_info.update(get_video_info(file_path))
            files.append(file_info)
        
        return {"files": files} if files else {"message": "No files found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {e}")

@app.delete("/api/files/{filename}")
async def delete_file(filename: str) -> None:
    "Delete a specific file from the uploads directory."

    file_path = upload_dir / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")
    try:
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file {filename}: {e}")

@app.post("/api/process/add/{filename}")
async def process_video(filename: str):
    "Add a video to the processing queue"

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
    "Get the status of a processing task."
    
    current_status = queue_manager.find_task_status(task_id)
    
    if not current_status:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task = queue_manager.get_task_status(task_id, current_status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return task

@app.get("/api/process/ready")
async def list_processed_files() -> dict:
    "List all processed video files."
    try:
        files = []
        for filename in os.listdir(output_dir):
            file_path = output_dir / filename
            if file_path.is_file():
                file_info = {
                    "filename": filename,
                    "size": format_size(file_path.stat().st_size)
                }
                if file_validator.validate_extension(filename):
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