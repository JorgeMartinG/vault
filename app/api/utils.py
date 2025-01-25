import json
import subprocess
from pathlib import Path

def format_size(size: str) -> str:
    """Converts a size in bytes to a readable representation (B, KB, MB, GB, TB)."""

    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}".rstrip("0").rstrip(".")
        size /= 1024
    return f"{size:.2f} TB"


def get_video_info(file_path: Path) -> dict:
    """Extract technical information from a video file using ffprobe."""

    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'stream', '-of', 'json', str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        ffprobe_output = json.loads(result.stdout)
        video_info = {"video_streams": [], "audio_streams": []}

        for stream in ffprobe_output.get("streams", []):
            if stream["codec_type"] == "video":
                fps_fraction = stream.get("avg_frame_rate", "0/1")
                fps = eval(fps_fraction)
                video_info["video_streams"].append(
                    {
                        "codec": stream.get("codec_name"),
                        "resolution": f"{stream.get('width')}x{stream.get('height')}",
                        "fps": f"{round(fps,2)} fps",
                    }
                )

            elif stream["codec_type"] == "audio":
                video_info["audio_streams"].append(
                    {
                        "codec": stream.get("codec_name"),
                        "language": stream.get("tags", {}).get("language", "Unknown"),
                    }
                )

        return video_info

    except Exception as e:
        return {"error": f"Failed to retrieve video info: {str(e)}"}
