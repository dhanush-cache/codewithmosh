from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import requests
import yt_dlp  # type: ignore
from tqdm import tqdm

from seedr.account import SeedrAccount
from seedr.path import SeedrFolder
from utils.configs import DOWNLOADS, TEMP


def download_video(url: str, path: Path = DOWNLOADS):
    """
    Downloads a video from the given URL to the specified path.

    Args:
        url (str): The URL of the video to download.
        path (Path, optional): The directory or file path where the video will be saved.
                               If a directory is provided, the video will be saved with
                               its title and extension. Defaults to DOWNLOADS.

    Raises:
        Exception: If the download fails for any reason.
    """
    outtmpl = str(path / "%(title)s.%(ext)s") if path.is_dir() else str(path)
    folder = path if path.is_dir() else path.parent
    folder.mkdir(parents=True, exist_ok=True)
    opts = {"outtmpl": outtmpl}
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])  # type: ignore


def download_magnet(magnet: str) -> Path:
    """
    Downloads files from a magnet link using the Seedr service.

    Args:
        magnet (str): The magnet link to download.

    Returns:
        Path: The path to the directory where the files are downloaded.
    """
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
    """
    Downloads a file from the given URL and saves it as a temporary file with the specified suffix.

    Args:
        url (str): The URL of the file to download.
        suffix (str, optional): The suffix for the temporary file. Defaults to ".zip".

    Returns:
        Path: The path to the downloaded temporary file.

    Raises:
        HTTPError: If the HTTP request returned an unsuccessful status code.
    """
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
