from typing import Iterable

from seedr.account import SeedrAccount

account = SeedrAccount()


class SeedrFile:
    def __init__(self, file_id: int) -> None:
        self.id = file_id
        self.__file_info = account.fetch_file(self.id)
        self.name = self.__file_info["name"]
        self.url = self.__file_info["url"]
        self.path = ""

    def set_path(self, path: str = "") -> None:
        self.path = path

    def __str__(self) -> str:
        return self.name


class SeedrFolder:
    def __init__(self, folder_id: int = 0) -> None:
        self.id = folder_id
        self.__contents = account.list_contents(self.id)
        self.name = self.__get_name()
        self.path = self.__contents["fullname"]

    def __get_name(self) -> str:
        name = self.__contents["name"]
        return name if name else "root"

    def get_subfolders(self) -> Iterable["SeedrFolder"]:
        folders = self.__contents["folders"]
        return (SeedrFolder(folder["id"]) for folder in folders)

    def get_files(self) -> Iterable[SeedrFile]:
        files = self.__contents["files"]
        return (SeedrFile(file["folder_file_id"]) for file in files)

    def traverse(self) -> Iterable[SeedrFile]:
        for file in self.get_files():
            file.set_path(f"{self.path}/{file.name}")
            yield file
        for folder in self.get_subfolders():
            yield from folder.traverse()

    def __str__(self) -> str:
        return self.name
