import time
import logging
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime

from queue import QueueManager
from processor import VideoProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('ProcessorDaemon')

class ProcessorDaemon:
    """
    Daemon that manages video processing queue
    """
    def __init__(self, config: dict):
        self.config = config
        self.queue_manager = QueueManager(Path(config["path"]["queue"]))
        self.processor = VideoProcessor(
            Path(config["path"]["uploads"]),
            Path(config["path"]["processed"])
        )
        self.max_workers = config["processing"]["max_workers"]
        self.check_interval = config["processing"]["check_interval"]
        self.active_workers = 0
        self.lock = threading.Lock()
        self.running = False
        
    def start(self):
        """Start the daemon process"""
        self.running = True
        threading.Thread(target=self._process_queue, daemon=True).start()
        logger.info("Processor daemon started")
        
    def stop(self):
        """Stop the daemon process"""
        self.running = False
        logger.info("Processor daemon stopped")
        
    def _process_queue(self):
        """Main queue processing loop"""
        while self.running:
            if self.active_workers < self.max_workers:
                self._process_next_task()
            time.sleep(self.check_interval)
            
    def _process_next_task(self):
        """Process the next task in the queue"""
        with self.lock:
            if self.active_workers >= self.max_workers:
                return
            self.active_workers += 1
        
        try:
            queue_data = self.queue_manager._load_queue()
            
            if not queue_data["pending"]:
                return
            
            task = queue_data["pending"].pop(0)
            task["status"] = "processing"
            task["started_at"] = datetime.now().isoformat()
            queue_data["processing"].append(task)
            self.queue_manager._save_queue(queue_data)
            
            logger.info(f"Starting task {task['id']}")
            result = self.processor.process(task['filename'])
            
            self._update_task_status(task["id"], result)
            logger.info(f"Completed task {task['id']}")
            
        except Exception as e:
            logger.error(f"Task processing error: {str(e)}")
            if 'task' in locals():
                self._update_task_status(task["id"], {
                    "success": False,
                    "error": str(e)
                })
        finally:
            with self.lock:
                self.active_workers -= 1

    def _update_task_status(self, task_id: str, result: dict) -> None:
        """Update task status in queue"""
        queue_data = self.queue_manager._load_queue()
        for idx, proc_task in enumerate(queue_data["processing"]):
            if proc_task["id"] == task_id:
                if result["success"]:
                    proc_task["status"] = "completed"
                    proc_task["completed_at"] = datetime.now().isoformat()
                else:
                    proc_task["status"] = "error"
                    proc_task["error"] = result.get("error", "Unknown error")
                
                queue_data["completed"].append(proc_task)
                queue_data["processing"].pop(idx)
                break
        
        self.queue_manager._save_queue(queue_data)
