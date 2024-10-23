from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Generator, Union
from zipfile import ZipFile

from natsort import natsorted
from tqdm import tqdm

from ffmpeg import ffprocess


def get_videos(zip_ref: ZipFile) -> Generator:
    archived_videos = (
        video
        for video in natsorted(zip_ref.namelist())
        if video.endswith(".mp4") or video.endswith(".mkv")
    )
    return archived_videos


def get_sub_from_archive(video_path: str, zip_ref: ZipFile) -> Union[Path, None]:
    subtitle_suffixes = [".srt", ".vtt"]
    for suffix in subtitle_suffixes:
        subtitle_target = str(Path(video_path).with_suffix(suffix))
        if subtitle_target in zip_ref.namelist():
            subtitles = NamedTemporaryFile("wb", suffix=suffix)
            subtitles.write(zip_ref.open(subtitle_target).read())
            return Path(subtitles.name)
    return None


def extract_videos(source: Path, target_list: Generator, ffmpeg=False):
    with ZipFile(source) as zip_ref:
        archived_videos = get_videos(zip_ref)
        for video_path, target in tqdm(list(zip(archived_videos, target_list))):
            archived_video = zip_ref.open(video_path)
            archived_path = Path(archived_video.name)
            subtitles = get_sub_from_archive(video_path, zip_ref)
            target.parent.mkdir(parents=True, exist_ok=True)
            if ffmpeg:
                with NamedTemporaryFile(suffix=archived_path.suffix) as temp:
                    video = Path(temp.name)
                    video.write_bytes(archived_video.read())
                    ffprocess(video, target, subtitles)
            else:
                target.write_bytes(archived_video.read())
                if subtitles:
                    target.with_suffix(subtitles.suffix).write_bytes(
                        subtitles.read_bytes()
                    )

        remaining_source = list(archived_videos)
        remaining_target = list(target_list)
        if remaining_source or remaining_target:
            print("Left off files:")
            print(remaining_source)
            print(remaining_target)


def extract_non_videos(source: Path, target: Path):
    with ZipFile(source) as zip_ref:
        archived_videos = (
            video
            for video in natsorted(zip_ref.namelist())
            if video not in get_videos(zip_ref)
        )
        for video in archived_videos:
            zip_ref.extract(video, target / "Files")
