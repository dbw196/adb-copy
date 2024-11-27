from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import os
import posixpath
import adbtools
from typing import Final


class PathInfo(ABC):

    _path: str
    _name: str
    _exists: bool
    _is_file: bool
    _is_dir: bool
    _modification_time: float
    _size: int

    def get_name(self):
        return self._name

    def get_path(self):
        return self._path

    def exists(self) -> bool:
        return self._exists

    def is_file(self) -> bool:
        return self._exists and self._is_file

    def is_dir(self) -> bool:
        return self._exists and self._is_dir

    def get_modification_time(self) -> datetime:
        return self._modification_time if self._exists else None

    def get_size(self) -> int:
        return self._size if self._exists else None

    @abstractmethod
    def get_md5_sum(self) -> str:
        pass

    @abstractmethod
    def list_files(self) -> list:
        pass

    def __repr__(self) -> str:
        return (f"<{type(self).__name__} name='{self.get_name()} path='{self.get_path()}' "
                f"exists={self.exists()} is_file={self.is_file()} "
                f"is_dir={self.is_dir()} "
                f"modification_time={self.get_modification_time()} "
                f" size={self.get_size()}>")


class LocalPathInfo(PathInfo):

    def __init__(self, arg: str | os.DirEntry):
        if type(arg) is str:
            self._path = os.path.normpath(arg)
            self._name = os.path.basename(self._path)
            self._exists = os.path.exists(self._path)
            if (self._exists):
                self._is_file = os.path.isfile(self._path)
                self._is_dir = os.path.isdir(self._path)
                self._modification_time = datetime.fromtimestamp(
                    os.path.getmtime(self._path))
                self._size = os.path.getsize(self._path)
        else:
            self._path = arg.path
            self._name = arg.name
            self._exists = True
            self._is_file = arg.is_file()
            self._is_dir = arg.is_dir()
            stat_result = arg.stat()
            self._modification_time = datetime.fromtimestamp(
                stat_result.st_mtime)
            self._size = stat_result.st_size

    def get_md5_sum(self) -> str:
        pass

    def list_files(self) -> list[PathInfo]:
        return [LocalPathInfo(dir_entry) for dir_entry in os.scandir(self._path)]


class AdbPathInfo(PathInfo):
    LS_OUTPUT_COLUMNS: Final[int] = 8

    def __init__(self, path: str, ls_output: str = None):
        if ls_output is None:
            self._path: str = posixpath.normpath(path)
            self._name = posixpath.basename(self._path)
            self._exists = adbtools.exists(self._path)
            if self._exists:
                self._is_file = adbtools.is_file(self._path)
                self._is_dir = adbtools.is_dir(self._path)
                if self._is_file:
                    ls_output = adbtools.ls_ll(self._path)[0]
                else:
                    parent = posixpath.dirname(self._path)
                    ls_output = next(line for line in adbtools.ls_ll(
                        parent) if posixpath.split(AdbPathInfo.__split_ls_output(line)[-1])[-1] == self._name)
                (_, _, self._size, self._modification_time,
                 _) = AdbPathInfo.__parse_ls_output(ls_output)

        else:
            self._exists = True
            (self._is_file, self._is_dir, self._size, self._modification_time,
             self._name) = AdbPathInfo.__parse_ls_output(ls_output)
            self._path: str = posixpath.join(path, self._name)

    def __split_ls_output(ls_output: str):
        return ls_output.split(maxsplit=AdbPathInfo.LS_OUTPUT_COLUMNS)

    def __parse_ls_output(ls_output: str) -> tuple[bool, bool, int, datetime, str]:
        print("parsing " + ls_output)
        type_and_perms, _, _, _, size, date, time, timezone, filename = AdbPathInfo.__split_ls_output(
            ls_output)
        date_time_str = f"{date} {time}{timezone}"
        date_time = datetime.fromisoformat(date_time_str)
        return (type_and_perms[0] == "-",
                type_and_perms[0] == "d",
                int(size),
                date_time,
                filename
                )

    def get_md5_sum(self) -> str:
        return adbtools.md5_sum(self._path)

    def list_files(self) -> list[PathInfo]:
        ls_output_list: list[str] = adbtools.ls_ll(self._path)
        ls_output_list = ls_output_list[1:]  # first output is total amount
        return [AdbPathInfo(self._path, ls_output) for ls_output in ls_output_list]
