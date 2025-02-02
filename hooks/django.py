from pathlib import Path

from ffmpeg import get_blank_video
from utils.archive import add_file_to_zip, merge_zips


def main(*archives: Path) -> Path:
    merged = merge_zips(*archives)
    pattern = "Part 2/lesson76.mp4"
    add_file_to_zip(merged, get_blank_video(10), pattern)
    return merged
