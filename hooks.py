import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from tqdm import tqdm

from ffmpeg import get_blank_video
from main import HOME

TEMP = HOME / "tmp"

TEMP.mkdir(parents=True, exist_ok=True)


def merge_zips(*archives):
    with TemporaryDirectory(dir=TEMP) as temp_dir:
        for i, archive in enumerate(tqdm(archives, desc="Unpacking archives")):
            temp_dir = Path(temp_dir)
            with zipfile.ZipFile(archive, "r") as zip_ref:
                zip_ref.extractall(temp_dir / f"{i}")

        with NamedTemporaryFile(dir=TEMP, delete=False, suffix=".zip") as output_zip:
            with zipfile.ZipFile(output_zip, "w") as zipf:
                for file in tqdm(list(temp_dir.rglob("*")), desc="Repacking archive"):
                    zipf.write(file, file.relative_to(temp_dir))
            return Path(output_zip.name)


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
