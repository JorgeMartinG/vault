import subprocess
from pathlib import Path
from .queue import QueueManager
from .logger import VideoLogger

class VideoProcessor:
    """Video processor function that handles video processing tasks."""
    
    def __init__(self, input_dir: Path, output_dir: Path, queue_manager: QueueManager, logger: VideoLogger):
        """Initialize video processor."""

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.queue_manager = queue_manager
        self.logger = logger
        
        self.output_dir.mkdir(parents=True, exist_ok=True) # Create processed directory if not exists.
    
    def process_video(self, filename: str, task_id: str) -> bool:
        """Process a video file using ffmpeg."""

        input_file = self.input_dir / filename
        output_filename = f"processed_{Path(filename).stem}.ts"
        output_file = self.output_dir / output_filename
        
        # Validación básica de archivos
        if not input_file.exists():
            self.logger.log_error(f"Input file not found: {input_file}")
            self.queue_manager.update_task_status(
                task_id, 
                "error",
                "Input file not found or was deleted"
            )
            return False
        
        if output_file.exists():
            self.logger.log_error(f"Output file already exists: {output_file}")
            self.queue_manager.update_task_status(
                task_id, 
                "error",
                "Output file already exists"
            )
            return False
        
        can_process, message = self.queue_manager.validate_file(filename)
        if not can_process:
            self.logger.log_processing_error(filename, f"Validation failed: {message}") # Verify if can be processed by Queue manager.
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
                error_msg = "The video could not be processed due to an unexpected error."
                self.logger.log_processing_error(filename, f"{error_msg}")
                if output_file.exists():
                    output_file.unlink()
                return False
            
            self.logger.log_processing_complete(filename)
            return True
            
        except Exception as e:
            self.logger.log_processing_error(filename, str(e))
            if output_file.exists():
                output_file.unlink()
            return False 

    def _handle_error(self, filename: str, error_msg: str, output_file: Path) -> None:
        """Handle processing errors and cleanup."""
        # Mensaje de error más conciso
        error = "Error en la conversión del video"
        self.logger.log_error(f"Error processing {filename}: {error}")
        
        if output_file.exists():
            output_file.unlink() 