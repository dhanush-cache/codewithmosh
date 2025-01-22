import zipfile
from pathlib import Path

from ffmpeg import get_blank_video
from utils.archive import merge_zips


def add_file_to_zip(zip_path: Path, file_to_add: Path, after: str) -> None:
    """
    Adds a file to an existing ZIP archive, renaming it based on an existing file in the archive.

    Args:
        zip_path (Path): The path to the ZIP archive.
        file_to_add (Path): The path to the file to be added to the ZIP archive.
        after (str): A string to match against existing file names in the ZIP archive. The new file will be renamed based on the first match.

    Returns:
        None
    """
    with zipfile.ZipFile(zip_path, "a") as zipf:
        target_file = Path(next(filter(lambda x: after in x, zipf.namelist())))
        arcname = target_file.with_stem(target_file.stem + "0")
        zipf.write(file_to_add, arcname=arcname)


def cpp(*archives: Path) -> Path:
    merged = merge_zips(*archives)
    pattern = "62_14_Parsing_Strings.mp4"
    add_file_to_zip(merged, get_blank_video(10), pattern)
    return merged


def django(*archives: Path) -> Path:
    merged = merge_zips(*archives)
    pattern = "Part 2/lesson76.mp4"
    add_file_to_zip(merged, get_blank_video(10), pattern)
    return merged
