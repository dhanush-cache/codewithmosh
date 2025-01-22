import zipfile
from pathlib import Path

from ffmpeg import get_blank_video
from utils.archive import merge_zips


def add_file_to_zip(zip_path, file_to_add, after):
    with zipfile.ZipFile(zip_path, "a") as zipf:
        target_file = Path(next(filter(lambda x: after in x, zipf.namelist())))
        arcname = target_file.with_stem(target_file.stem + "0")
        zipf.write(file_to_add, arcname=arcname)


def cpp(*archives):
    archives = [Path(archive) for archive in archives]
    merged = merge_zips(*archives)
    pattern = "62_14_Parsing_Strings.mp4"
    add_file_to_zip(merged, get_blank_video(10), pattern)
    return merged


def django(*archives):
    archives = [Path(archive) for archive in archives]
    merged = merge_zips(*archives)
    pattern = "Part 2/lesson76.mp4"
    add_file_to_zip(merged, get_blank_video(10), pattern)
    return merged
