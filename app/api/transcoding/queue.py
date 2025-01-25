import json
import uuid
import shutil
from pathlib import Path
from datetime import datetime

class QueueManager:
    "Queue manager for video processing tasks."
    
    def __init__(self, queue_file: Path, config: dict):
        "Initialize the queue manager."
        self.queue_file = queue_file
        self.config = config
        self.path = self.config["path"]
        self._create()

    # --------------- [Private Methods] ---------------
    def _create(self) -> None:
        "Create queue file if not exists."
        if not self.queue_file.exists():
            initial_queue = {"pending": [], "processing": [], "completed": [], "error": []} # Create initial dict in case file does not exist.
            self.queue_file.parent.mkdir(parents=True, exist_ok=True) # Create parent directory if not exists.
            self._save(initial_queue) # Save initial dict to queue file using "_save" method.
    
    def _save(self, queue_data: dict) -> None:
        "Dump data into the queue file."
        with open(self.queue_file, 'w') as f:
            json.dump(queue_data, f, indent=4)
    
    def _load(self) -> dict:
        "Read the current status of the queue file."
        with open(self.queue_file, 'r') as f:
            return json.load(f)
        
    # --------------- [Task methods] ---------------

    def find_task_status(self, task_id: str, queue_data: dict) -> str:
        """Find current status of a task."""

        statuses = ["pending", "processing", "completed", "error"]
        for status in statuses:
            if any(task["id"] == task_id for task in queue_data[status]): # Iterate between all possible states.
                return status
        return None
    
    def get_task_status(self, task_id: str, status: str, queue_data: dict) -> dict:
        """Get task from a specific status list."""

        for task in queue_data[status]:
            if task["id"] == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: str, new_status: str, error_message: str = None) -> bool:
        """Update task status."""

        queue_data = self._load() # load queue on memory.
        current_status = self.find_task_status(task_id, queue_data) # Get task status by task id.
        
        if not current_status:
            return False
            
        task = self.get_task_status(task_id, current_status, queue_data) 
        if not task: 
            return False
        
        queue_data[current_status].remove(task)
        
        task["status"] = new_status
        task["updated_at"] = datetime.now().isoformat()
        
        if new_status == "error" and error_message:
            task["error_message"] = error_message
        
        queue_data[new_status].append(task)
        self._save(queue_data)
        return True

    def add_task(self, filename: str) -> str:
        """Add new task to the queue."""

        task_id = str(uuid.uuid4()) # Get random id with uuid module.
        now = datetime.now().isoformat()
        
        task = {
            "id": task_id,
            "filename": filename,
            "status": "pending",
            "created_at": now,
            "updated_at": now
        }
        
        queue_data = self._load()
        queue_data["pending"].append(task)
        self._save(queue_data)
        
        return task_id

    def check_task(self, filename: str) -> tuple[bool, str]:
        """Verify if a task is already on the queue."""

        queue_data = self._load()
        
        for status in ["pending", "processing", "completed"]:
            for task in queue_data[status]:
                if task["filename"] == filename:
                    return True, status
        
        return False, ""
    
    # --------------- [Class methods] ---------------

    def validate_file(self, filename: str) -> tuple[bool, str]:
        """Validate if file can be processed."""

        try:
            file_path = Path(self.path["uploads"]) / filename
            if not file_path.exists():
                return False, "File not found"

            file_size = file_path.stat().st_size # Get file size in bytes (Pathlib).
            required_space = file_size * 2
            output_dir = Path(self.path["processed"])
            free_space = shutil.disk_usage(output_dir).free # Get free space in directory in bytes (Shutil).

            if free_space <= required_space:
                return False, "Not enough disk space"
            return True, "OK"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
