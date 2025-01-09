import subprocess
from pathlib import Path
from typing import Dict, Optional
from logger import setup_logger

logger = setup_logger('VideoProcessor', Path('/var/www/vault/app/logs'))

class VideoProcessor:
    """
    Handles the FFmpeg processing of video files
    """
    def __init__(self, input_path: Path, output_path: Path):
        self.input_path = input_path
        self.output_path = output_path
        
    def process(self, filename: str) -> Dict:
        """
        Process a video file using FFmpeg with predefined parameters
        
        Args:
            filename (str): Name of the file to process
            
        Returns:
            Dict: Processing result with status and error message if any
        """
        input_file = self.input_path / filename
        output_name = f"{filename.rsplit('.', 1)[0]}_multi.ts"
        output_file = self.output_path / output_name
        
        if not input_file.exists():
            return {
                "success": False,
                "error": f"Input file {filename} not found"
            }
            
        try:
            cmd = [
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
            
            logger.info(f"Starting processing of {filename}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"Successfully processed {filename}")
            
            return {
                "success": True,
                "output_file": output_name
            }
            
        except subprocess.CalledProcessError as e:
            error_msg = f"FFmpeg error: {e.stderr}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
