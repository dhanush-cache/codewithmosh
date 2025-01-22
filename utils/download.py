from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import requests
import yt_dlp  # type: ignore
from tqdm import tqdm

from seedr.account import SeedrAccount
from seedr.path import SeedrFolder
from utils.configs import TEMP


def download_video(url: str, path: Path = Path("/sdcard/Download")):
    outtmpl = str(path / "%(title)s.%(ext)s") if path.is_dir() else str(path)
    folder = path if path.is_dir() else path.parent
    folder.mkdir(parents=True, exist_ok=True)
    opts = {"outtmpl": outtmpl}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])  # type: ignore


def download_magnet(magnet: str) -> Path:
    target = Path(TemporaryDirectory(dir=TEMP, delete=False).name)
    account = SeedrAccount()
    folder_id = account.add_torrent(magnet)
    folder = SeedrFolder(folder_id)
    for file in folder.traverse():
        url = file.url
        path = target / file.path
        download_video(url, path)
    return target


def download_archive(url: str, suffix: str = ".zip") -> Path:
    file = Path(NamedTemporaryFile(dir=TEMP, suffix=suffix).name)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with file.open("wb") as f:
            total_size = int(r.headers.get("content-length", 0))
            with tqdm(
                total=total_size, unit="B", unit_scale=True, desc="Downloading archive"
            ) as pbar:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
    return file
