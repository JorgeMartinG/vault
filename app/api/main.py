import aiofiles
import json
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import List
from .tools import get_video_info, format_size


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

with open("/var/www/vault/app/api/config/config.json") as config_file:
    config = json.load(config_file)

cors_config = config["CORS"]

app.add_middleware(
    CORSMiddleware, 
    allow_origins=cors_config["origins"],
    allow_methods=cors_config["methods"],
    allow_headers=cors_config["headers"],
    allow_credentials=True,
)

upload_dir = Path(config["path"]["uploads"]).resolve()
upload_dir.mkdir(parents=True, exist_ok=True)


@app.post("/api/uploads/")
async def create_upload_file(file_uploads: List[UploadFile] = File(...)) -> list:

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

    try:
        files = []

        for filename in os.listdir(upload_dir):
            file_path = upload_dir / filename

            if file_path.is_file():
                file_info = {"filename": filename, "filesize": format_size(file_path.stat().st_size)}
            
            if filename.lower().endswith(('.mp4', '.mkv', '.ts')):
                file_info.update(get_video_info(file_path))

            files.append(file_info)

        if not files:
            return {"message": "No files found"}

        return {"files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {e}")


@app.delete("/api/files/{filename}")
async def delete_file(filename: str) -> None:

    file_path = upload_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"File {filename} not found")

    try:
        os.remove(file_path)
        return {"message": f"File {filename} deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file {filename}: {e}")

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
