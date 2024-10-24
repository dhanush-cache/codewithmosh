from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List
from zipfile import ZipFile


class MoshZip(ZipFile):
    def namelist_from_ext(self, *extensions: str) -> List[str]:
        return [file for file in self.namelist() if Path(file).suffix in extensions]

    def extract_subtitles(self, video_path: str) -> Path:
        archived_subs = self.namelist_from_ext(".srt", ".vtt", ".ass")
        prefix = str(Path(video_path).with_suffix(""))
        for archived_sub in archived_subs:
            if archived_sub.startswith(prefix):
                subtitle = Path(
                    NamedTemporaryFile(suffix=Path(archived_sub).suffix).name
                )
                subtitle.write_bytes(self.read(archived_sub))
                return subtitle
