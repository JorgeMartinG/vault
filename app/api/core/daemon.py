import time
import threading
from .manager import QueueManager
from .logging import VideoLogger
from .process import VideoProcessor
from .validate import FileValidator

class ProcessorDaemon:
    """Daemon that manages the video processing queue."""
    
    def __init__(self, queue_manager: QueueManager, video_processor: VideoProcessor, file_validator: FileValidator, logger: VideoLogger, check_interval: int = 1):
        """
        Initialize the processor daemon.
        
        Args:
            queue_manager: Instance of QueueManager for task handling
            video_processor: Instance of VideoProcessor for video processing
            logger: Instance of VideoLogger for logging
            check_interval: How often to check the queue (in seconds)
        """
        self.queue_manager = queue_manager
        self.video_processor = video_processor
        self.file_validator = file_validator
        self.logger = logger
        self.check_interval = check_interval
        self.is_running = False
        self.thread = None
        
    def start(self):
        """Start the daemon process in a separate thread."""
        self.logger.log_info("Starting processor daemon")
        self.is_running = True
        self.thread = threading.Thread(target=self._process_queue)
        self.thread.daemon = True  # El thread se cerrará cuando el programa principal termine
        self.thread.start()
        
    def stop(self):
        """Stop the daemon process."""
        self.logger.log_info("Stopping processor daemon")
        self.is_running = False
        if self.thread:
            self.thread.join()  # Esperar a que el thread termine
        
    def _process_queue(self):
        """Main processing loop that checks and processes the queue."""

        while self.is_running:
            try:
                queue_data = self.queue_manager._load()
                
                # Procesar tareas pendientes (ya ordenadas por prioridad)
                for task in queue_data["pending"]:
                    # Actualizar estado a procesando antes de validar
                    self.queue_manager.update_task_status(task["id"], "processing")
                    
                    # Procesar el video
                    success = self.video_processor.process_video(
                        task["filename"],
                        task["id"]
                    )
                    
                    # Actualizar estado final
                    if success:
                        self.queue_manager.update_task_status(task["id"], "completed")
                    else:
                        self.queue_manager.update_task_status(task["id"], "error")
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.log_error(f"Error in processing loop: {str(e)}")
                time.sleep(self.check_interval) 