from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
from zipfile import ZipFile

from natsort import natsorted


class MoshZip(ZipFile):
    """
    A class that extends ZipFile to provide additional functionality for handling
    specific file types and extracting subtitles.

    Methods
    -------
    namelist_from_ext(*extensions: str) -> List[str]:
        Returns a list of file names in the archive that have the specified extensions.

    extract_subtitles(video_path: str) -> Path:
        Extracts the subtitle file corresponding to the given video file path from the archive.
    """

    def namelist_from_ext(self, *extensions: str) -> List[str]:
        """
        Generate a list of file names from the archive that match the given extensions.

        Args:
            extensions (str): Variable length argument list of file extensions to filter by.

        Returns:
            List[str]: A list of file names sorted in natural order that have the specified extensions.
        """
        return [
            file
            for file in natsorted(self.namelist())
            if Path(file).suffix in extensions
        ]

    def extract_subtitles(self, video_path: str) -> Path | None:
        """
        Extracts subtitles from an archive that match the given video path.

        This method searches for subtitle files within the archive that have the same
        base name as the provided video path and one of the specified subtitle file
        extensions (".srt", ".vtt", ".ass"). If a matching subtitle file is found,
        it is extracted to a temporary file and returned.

        Args:
            video_path (str): The path to the video file for which to extract subtitles.

        Returns:
            Path | None: The path to the extracted subtitle file if found, otherwise None.
        """
        archived_subs = self.namelist_from_ext(".srt", ".vtt", ".ass")
        prefix = str(Path(video_path).with_suffix(""))
        for archived_sub in archived_subs:
            if archived_sub.startswith(prefix):
                subtitle = Path(
                    NamedTemporaryFile(suffix=Path(archived_sub).suffix).name
                )
                subtitle.write_bytes(self.read(archived_sub))
                return subtitle
