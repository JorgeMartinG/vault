from pathlib import Path
import shutil

class FileValidator:
    "Validator for video processing operations."

    ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".ts", ".flv"}
    
    def __init__(self, path_config: dict):
        self.path_config = path_config
        self.uploads_dir = Path(path_config["uploads"])
        self.processed_dir = Path(path_config["processed"])

    def validate_extension(self, filename: str) -> tuple[bool, str]:
        "Validate if file extension is allowed."

        extension = Path(filename).suffix.lower()
        if extension not in self.ALLOWED_VIDEO_EXTENSIONS:
            return False, f"Invalid file extension: {extension}: Allowed extensions: {', '.join(self.ALLOWED_VIDEO_EXTENSIONS)}"
        return True, "OK"
    
    def validate_space(self, filename: str) -> tuple[bool, str]:
        "Validate if file size is allowed."
        
        try:
            output_dir = Path(self.processed_dir)
            if not output_dir.exists():
                output_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = Path(self.uploads_dir) / filename
            if not file_path.exists():
                return False, "File not found"

            file_size = file_path.stat().st_size

            required_space = file_size * 2
            available_space = shutil.disk_usage(output_dir).free

            if available_space <= required_space:
                return False, "Not enough disk space"
            return True, "OK"
            
        except Exception as e:
            return False, f"Available space validation error: {str(e)}"
    
    def validate_output_file(self, output_file: Path) -> tuple[bool, str]:
        "Validate if output file already exists."

        if output_file.exists():
            return False, "Output file already exists"
        return True, "OK"
    
    def validate(self, filename: str, output_file: Path) -> tuple[bool, str]:
        "Validate if file is allowed to be processed."

        valid_extension, message = self.validate_extension(filename)
        if not valid_extension:
            return False, message
        
        valid_space, message = self.validate_space(filename)
        if not valid_space:
            return False, message
        
        valid_output_file, message = self.validate_output_file(output_file)
        if not valid_output_file:
            return False, message
        
        return True, "OK"