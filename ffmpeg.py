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
    result = subprocess.run(
        ["ffprobe", f"{video}"],
        capture_output=True,
        check=True,
        text=True,
    )
    return "subtitle" in result.stderr.lower()


def ffprocess(video: Path, target: Path, timestamp: int, subtitles: Path | None = None):
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
    pattern = r"^\d+\s*-\s*"
    title = re.sub(pattern, "", path.stem)
    comment = re.sub(pattern, "", path.parent.stem)
    return title, comment
