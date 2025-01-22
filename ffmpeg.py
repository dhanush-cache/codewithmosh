import re
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

ffmpeg = ["ffmpeg", "-y"]
_metadata = [
    "-map_metadata",
    "-1",
    "-map_metadata:s",
    "-1",
    "-map_metadata:g",
    "-1",
    "-map_chapters",
    "-1",
    "-map_chapters:s",
    "-1",
    "-map_chapters:g",
    "-1",
]


def get_thumb(video: Path, timestamp: int) -> Path:
    """
    Extracts a thumbnail image from a video at a specified timestamp.

    Args:
        video (Path): The path to the video file.
        timestamp (int): The timestamp (in seconds) at which to extract the thumbnail.

    Returns:
        Path: The path to the extracted thumbnail image.
    """
    inputs = ["-i", f"{video}"]
    target = NamedTemporaryFile(suffix=".jpeg").name
    extract = [
        "-ss",
        str(timestamp),
        "-vframes",
        "1",
    ]
    output = [target]
    command = ffmpeg + inputs + _metadata + extract + output
    subprocess.run(command, check=True, capture_output=True)
    return Path(target)


def has_embedded_subs(video: Path) -> bool:
    """
    Checks if a video file has embedded subtitles.

    Args:
        video (Path): The path to the video file.

    Returns:
        bool: True if the video has embedded subtitles, False otherwise.
    """
    result = subprocess.run(
        ["ffprobe", f"{video}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return "subtitle" in result.stderr.lower()


def ffprocess(video: Path, target: Path, timestamp: int, subtitles: Path | None = None):
    """
    Processes a video file using ffmpeg, adding metadata, subtitles, and a thumbnail.

    Args:
        video (Path): The path to the input video file.
        target (Path): The path to the output video file.
        timestamp (int): The timestamp (in seconds) to capture the thumbnail.
        subtitles (Path | None, optional): The path to the subtitles file. Defaults to None.

    Returns:
        str: The stderr output from the ffmpeg command.
    """
    inputs = ["-i", f"{video}"]
    if subtitles:
        inputs += ["-i", f"{subtitles}"]

    title, comment = get_metadata(target)
    metadata = [
        "-metadata",
        f"title={title}",
        "-metadata",
        f"comment={comment}",
        "-metadata:s:a:0",
        "language=en",
    ]
    if subtitles or has_embedded_subs(video):
        metadata += [
            "-metadata:s:s:0",
            "language=en",
        ]

    thumbnail = [
        "-attach",
        f"{get_thumb(video, timestamp)}",
        "-metadata:s:t",
        f"filename={title}",
        "-metadata:s:t",
        "mimetype=image/jpeg",
    ]

    mapping = ["-map", "0:v", "-map", "0:a"]
    if subtitles:
        mapping += ["-map", "1:s"]
    elif has_embedded_subs(video):
        mapping += ["-map", "0:s"]

    codec = ["-c", "copy"]
    if subtitles or has_embedded_subs(video):
        codec += ["-c:s", "srt"]

    output = [f"{target}"]

    command = (
        ffmpeg + inputs + mapping + codec + _metadata + metadata + thumbnail + output
    )

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stderr


def get_metadata(path: Path):
    """
    Extracts metadata from the given file path.

    Args:
        path (Path): The path to the file.

    Returns:
        tuple: A tuple containing the title and comment extracted from the file path.
    """
    pattern = r"^\d+\s*-\s*"
    title = re.sub(pattern, "", path.stem)
    comment = re.sub(pattern, "", path.parent.stem)
    return title, comment


def get_blank_video(duration: int) -> Path:
    """
    Generates a blank video file of the specified duration.

    This function creates a temporary MP4 file containing a blank video with a black screen
    and silent audio. The video has a resolution of 1920x1080 and uses the H.264 codec for
    video and AAC codec for audio.

    Args:
        duration (int): The duration of the blank video in seconds.

    Returns:
        Path: The file path to the generated blank video.
    """
    with NamedTemporaryFile(suffix=".mp4", delete=False) as temp_file:
        blank_video = Path(temp_file.name)
        command = ffmpeg + [
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s=1920x1080:d={duration}",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r=44100:cl=stereo",
            "-shortest",
            "-vf",
            "format=yuv420p",
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-t",
            str(duration),
            str(blank_video),
        ]
        subprocess.run(command, check=True, capture_output=True)
    return blank_video
