import json
import webbrowser
from pathlib import Path
from time import sleep, time
from typing import Any, Dict, List, cast
from urllib.parse import ParseResult, parse_qs, urlparse

import requests
from seedrcc import Login, Seedr  # type: ignore

from utils.general import copy_to_clipboard


class SeedrAccount:
    """Represents a seedr.cc user account."""

    token_file = Path.home() / ".cache" / "codewithmosh" / "token.txt"

    def __init__(self) -> None:
        self.token = self.__read_token()
        self.account = Seedr(self.token, callbackFunc=self.__update_token)
        if not self.is_active():
            self.token = self.login()
            self.account = Seedr(self.token, callbackFunc=self.__update_token)

    def is_active(self) -> bool:
        """Check whether the account token is active."""
        return self.account.testToken().get("result", False)

    def login(self) -> str:
        """Login to your seedr account."""
        seedr = Login()
        deviceCode = seedr.getDeviceCode()

        user_code = deviceCode["user_code"]
        copy_to_clipboard(user_code, "Authorization")
        webbrowser.open(deviceCode["verification_url"])

        sleep(10)
        while True:
            sleep(2)
            response = seedr.authorize(deviceCode["device_code"])  # type: ignore
            if "error" not in response:
                break

        token = str(seedr.token)
        self.__update_token(token)
        return token

    def get_torrents(self) -> List[Dict[Any, Any]]:
        """Get a list of active torrents."""
        return self.list_contents()["torrents"]

    def add_torrent(self, magnet_link: str) -> int:
        """Add torrent by its magnet link."""
        start_time = time()

        torrent_id = cast(
            Dict[Any, Any],
            self.account.addTorrent(magnet_link),  # type: ignore
        )["user_torrent_id"]
        torrents = self.get_torrents()
        fetched: bool = bool(torrents and torrents[0]["id"] == torrent_id)
        torrent = torrents[0] if fetched else None

        while True:
            sleep(2)
            if not self.get_torrents():
                if torrent:
                    return self.__get_id_from_torrent(torrent)
                return self.get_latest_folder_id()

            if (time() - start_time) > 60:
                raise TimeoutError("It's taking too long...")

    def get_latest_folder_id(self) -> int:
        """Get the folder id for the last added folder."""
        folders = self.list_contents()["folders"]
        return folders[-1]["id"]

    def get_top_file_url(self, folder_id: int = 0) -> str:
        if not folder_id:
            folder_id = self.get_latest_folder_id()
        files: List[Dict[Any, Any]] = self.list_contents(folder_id)["files"]
        files.sort(key=lambda file: file["size"], reverse=True)
        largest_file_id = files[0]["folder_file_id"]
        return cast(dict, self.account.fetchFile(largest_file_id))["url"]  # type: ignore

    def magnet_to_url(self, magnet_link: str) -> str:
        folder_id = self.add_torrent(magnet_link)
        return self.get_top_file_url(folder_id)

    def delete_folder(self, folder_id: int = 0) -> None:
        if "error" in self.list_contents(folder_id):
            raise KeyError("Folder does not exist.")
        self.account.deleteFolder(folder_id)  # type: ignore

    def list_contents(self, folder_id: int = 0) -> Dict[Any, Any]:
        return cast(Dict[Any, Any], self.account.listContents(folder_id))

    def fetch_file(self, file_id: int = 0) -> Dict[Any, Any]:
        return cast(Dict[Any, Any], self.account.fetchFile(file_id))  # type: ignore

    def __read_token(self) -> str:
        if self.token_file.exists():
            return self.token_file.read_text()
        return self.login()

    def __get_id_from_torrent(self, torrent: Dict[Any, Any]) -> int:
        progress_url = torrent["progress_url"]
        parsed = cast(ParseResult, urlparse(progress_url))
        url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

        queries = parse_qs(parsed.query)
        params = {key: value[0] for key, value in queries.items()}

        response = requests.get(url, params=params)
        torrent_info = json.loads(response.text.strip("?()"))
        folder_id = torrent_info["stats"]["folder_created"]
        return folder_id

    def __update_token(self, token: str) -> None:
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.token_file.write_text(token)
