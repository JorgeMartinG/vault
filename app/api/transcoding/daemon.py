import time
import threading
from .queue import QueueManager
from .process import VideoProcessor
from .logger import VideoLogger

class ProcessorDaemon:
    """Daemon that manages the video processing queue."""
    
    def __init__(self, queue_manager: QueueManager, video_processor: VideoProcessor, logger: VideoLogger, check_interval: int = 1):
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
                queue_data = self.queue_manager._load_queue()
                
                # Procesar tareas pendientes (ya ordenadas por prioridad)
                for task in queue_data["pending"]:
                    # Validar el archivo
                    can_process, message = self.queue_manager.validate_file(task["filename"])
                    if not can_process:
                        self.logger.log_error(f"Validation failed for {task['filename']}: {message}")
                        self.queue_manager.update_task_status(
                            task["id"], 
                            "error",
                            message
                        )
                        continue
                    
                    # Actualizar estado a procesando
                    self.queue_manager.update_task_status(task["id"], "processing")
                    self.logger.log_info(f"Processing {task['filename']}")
                    
                    # Procesar el video
                    success = self.video_processor.process_video(
                        task["filename"],
                        task["id"]
                    )
                    
                    # Actualizar estado final
                    if success:
                        self.queue_manager.update_task_status(task["id"], "completed")
                    else:
                        # Verificar si podemos reintentar
                        if task["retries"] < task["max_retries"]:
                            # Volver a pending con menor prioridad
                            new_priority = min(5, task["priority"] + 1)
                            self.queue_manager.update_task_status(
                                task["id"],
                                "pending",
                                f"Retry {task['retries'] + 1}/{task['max_retries']}"
                            )
                        else:
                            self.queue_manager.update_task_status(
                                task["id"],
                                "error",
                                "Max retries exceeded"
                            )
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.log_error(f"Error in processing loop: {str(e)}")
                time.sleep(self.check_interval) 