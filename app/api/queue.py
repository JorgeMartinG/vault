import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class QueueManager:
    def __init__(self, queue_path: Path):
        self.queue_path = queue_path
        self.queue_file = queue_path / "tasks.json"
        self._initialize_queue()
    
    def _initialize_queue(self) -> None:
        """Initialize the queue file if it does not exist"""
        self.queue_path.mkdir(parents=True, exist_ok=True)
        if not self.queue_file.exists():
            self._save_queue({
                "pending": [],
                "processing": [],
                "completed": []
            })
    
    def _load_queue(self) -> Dict:
        """Load the current state of the queue"""
        with open(self.queue_file, 'r') as f:
            return json.load(f)
    
    def _save_queue(self, queue_data: Dict) -> None:
        """Save the queue state"""
        with open(self.queue_file, 'w') as f:
            json.dump(queue_data, f, indent=4)
    
    def add_task(self, filename: str) -> str:
        """Add a new task to the queue"""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "filename": filename,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None
        }
        
        queue_data = self._load_queue()
        queue_data["pending"].append(task)
        self._save_queue(queue_data)
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Gets the status of a specific task"""
        queue_data = self._load_queue()
        
        for status in ["pending", "processing", "completed"]:
            for task in queue_data[status]:
                if task["id"] == task_id:
                    return task
        
        return None
    
    def cleanup_old_tasks(self, days: int = 7) -> None:
        """Remove completed tasks older than specified days"""
        queue_data = self._load_queue()
        current_time = datetime.now()
        
        def is_recent(task):
            completed_at = datetime.fromisoformat(task["completed_at"])
            return (current_time - completed_at).days < days
        
        queue_data["completed"] = [
            task for task in queue_data["completed"]
            if task["completed_at"] and is_recent(task)
        ]
        
        self._save_queue(queue_data)