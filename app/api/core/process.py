import subprocess
from pathlib import Path
from .logging import VideoLogger
from .manager import QueueManager
from .validate import FileValidator

class VideoProcessor:
    "Video processor function that handles video processing tasks."
    
    def __init__(self, input_dir: Path, output_dir: Path, queue_manager: QueueManager, file_validator: FileValidator, logger: VideoLogger):
        "Initialize video processor."

        self.uploads = Path(input_dir)
        self.processed = Path(output_dir)
        self.queue_manager = queue_manager
        self.file_validator = file_validator
        self.logger = logger
    
    def process_video(self, filename: str, task_id: str) -> bool:
        "Process a video file using ffmpeg."

        input_file = self.uploads / filename
        processed_filename = f"processed_{Path(filename).stem}.ts"
        output_file = self.processed / processed_filename

        valid, message = self.file_validator.validate(input_file, output_file)
        if not valid:
            self.logger.log_error(f"File validation failed: {message}")
            self.queue_manager.update_task_status(task_id, "error")
            return False
        
        try:
            command = [
                'ffmpeg', '-n',
                '-i', str(input_file),
                '-bsf:v', 'h264_mp4toannexb',
                '-profile:v', 'main', 
                '-crf', '20',
                '-codec:v', 'libx264',
                '-x264opts', 'keyint=100',
                '-preset', 'fast',
                '-codec:a', 'aac',
                '-map', 'v:0',
                '-map', '0:a',
                '-strict', '-2',
                '-sn',
                '-maxrate', '14M',
                '-bufsize', '1M',
                str(output_file)
            ]
            
            self.logger.log_processing_start(filename)
            
            result = subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode != 0:
                error_msg = f"FFmpeg error: {result.stderr}"
                self._handle_error(filename, error_msg, output_file)
                self.queue_manager.update_task_status(task_id, "error")
                return False
            
            self.logger.log_processing_complete(filename)
            return True
            
        except Exception as e:
            error_msg = f"Processing error: {str(e)}"
            self._handle_error(filename, error_msg, output_file)
            self.queue_manager.update_task_status(task_id, "error", error_msg)
            return False 

    def _handle_error(self, filename: str, error_msg: str, output_file: Path) -> None:
        "Handle processing errors and cleanup."

        self.logger.log_processing_error(filename, error_msg)
        if output_file.exists():
            output_file.unlink()