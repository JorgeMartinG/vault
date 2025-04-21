import logging
from pathlib import Path
from datetime import datetime

class VideoLogger:
    """Custom logger for video processing operations."""
    
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar un único logger
        self.logger = logging.getLogger('processing')
        self.logger.setLevel(logging.INFO)
        
        # Configurar el handler para el archivo
        log_file = log_dir / 'processing.log'
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Formato del log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def log_info(self, message: str):
        """Log información general."""
        self.logger.info(message)
    
    def log_error(self, message: str):
        """Log errores."""
        self.logger.error(message)
    
    def log_processing_start(self, filename: str):
        """Log inicio de procesamiento."""
        self.log_info(f"Started processing video: {filename}")
    
    def log_processing_complete(self, filename: str):
        """Log fin de procesamiento exitoso."""
        self.log_info(f"Successfully processed video: {filename}")
    
    def log_processing_error(self, filename: str, error: str):
        """Log error de procesamiento."""
        self.log_error(f"Error processing video {filename}: {error}") 