from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Generator

from natsort import natsorted
from tqdm import tqdm

from archive import MoshZip
from ffmpeg import ffprocess


def extract_videos(archive: Path, target_list: Generator, ffmpeg=False):
    with MoshZip(archive) as zip_ref:
        archived_videos = zip_ref.namelist_from_ext(".mp4", ".mkv")
        print("Processing videos...")
        for video_path, target in tqdm(list(zip(archived_videos, target_list))):
            archived_video = zip_ref.open(video_path)
            archived_path = Path(archived_video.name)
            subtitles = zip_ref.extract_subtitles(video_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            if ffmpeg:
                with NamedTemporaryFile(suffix=archived_path.suffix) as temp:
                    video = Path(temp.name)
                    video.write_bytes(archived_video.read())
                    ffprocess(video, target, subtitles)
                    continue
            target.write_bytes(archived_video.read())
            if subtitles:
                target.with_suffix(subtitles.suffix).write_bytes(subtitles.read_bytes())


def extract_non_videos(source: Path, target_dir: Path):
    with MoshZip(source) as zip_ref:
        non_videos = (
            video
            for video in natsorted(zip_ref.namelist())
            if video in zip_ref.namelist_from_ext(".zip", ".pdf")
        )
        print("\nProcessing other files...")
        for video in tqdm(non_videos):
            target = target_dir / "Files" / video.replace(":", "-")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zip_ref.read(video))
