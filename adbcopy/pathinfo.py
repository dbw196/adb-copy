from abc import ABC, abstractmethod
from datetime import datetime, timezone
import hashlib
import os
import posixpath
from adbcopy import adbtools
from typing import Final, cast
from logging import Logger, getLogger



logger: Logger = getLogger(__name__)

ADB_PATTERN: str = "adb:"


class PathInfo(ABC):

    _path: str
    _name: str
    _exists: bool
    _is_file: bool
    _is_dir: bool
    _modification_time: datetime
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
        return self._modification_time

    def get_size(self) -> int:
        return self._size

    @abstractmethod
    def get_md5_sum(self) -> str:
        pass

    @abstractmethod
    def list_dir(self) -> list["PathInfo"]:
        pass

    @abstractmethod
    def get_child(self, child) -> "PathInfo":
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
                self._modification_time = datetime.fromtimestamp(os.path.getmtime(self._path), tz=timezone.utc).replace(microsecond=0)
                self._size = os.path.getsize(self._path)
        else:
            arg = cast(os.DirEntry, arg)
            self._path = arg.path
            self._name = arg.name
            self._exists = True
            self._is_file = arg.is_file()
            self._is_dir = arg.is_dir()
            stat_result = arg.stat()
            self._modification_time = datetime.fromtimestamp(stat_result.st_mtime, tz=timezone.utc).replace(microsecond=0)
            self._size = stat_result.st_size

    def get_md5_sum(self) -> str:
        with open(self._path, 'rb') as f:
            data: bytes = f.read()
            return hashlib.md5(data).hexdigest()

    def list_dir(self) -> list[PathInfo]:
        return [LocalPathInfo(dir_entry) for dir_entry in os.scandir(self._path)]
    
    def get_child(self, child) -> PathInfo:
        return LocalPathInfo(os.path.join(self._path, child))
    



class AdbPathInfo(PathInfo):
    LS_OUTPUT_COLUMNS: Final[int] = 8

    def __init__(self, path: str, ls_output: str | None = None):
        if ls_output is None:
            self._path = posixpath.normpath(path)
            self._name = posixpath.basename(self._path)
            self._exists = adbtools.exists(self._path)
            if self._exists:
                self._is_file = adbtools.is_file(self._path)
                self._is_dir = adbtools.is_dir(self._path)
                if self._is_file:
                    ls_output = adbtools.ls_ll(self._path)[0]
                else:
                    parent = posixpath.dirname(self._path)
                    logger.debug("parent: %s", parent)
                    ls_output = next(line for line in adbtools.ls_ll(
                        parent) if posixpath.split(AdbPathInfo.__split_ls_output(line)[-1])[-1] == self._name)
                (_, _, self._size, self._modification_time,
                 _) = AdbPathInfo.__parse_ls_output(ls_output)

        else:
            self._exists = True
            self._is_file, self._is_dir, self._size, self._modification_time, self._name = AdbPathInfo.__parse_ls_output(ls_output)
            self._path = posixpath.join(path, self._name)

    @staticmethod
    def __split_ls_output(ls_output: str):
        return ls_output.split(maxsplit=AdbPathInfo.LS_OUTPUT_COLUMNS)

    @staticmethod
    def __parse_ls_output(ls_output: str) -> tuple[bool, bool, int, datetime, str]:
        logger.debug("parsing %s", ls_output)
        type_and_perms, _, _, _, size, date, time, tz, filename = AdbPathInfo.__split_ls_output(
            ls_output)
        date_time_str = f"{date} {time}{tz}"
        date_time: datetime = datetime.fromisoformat(date_time_str).replace(microsecond=0).astimezone(timezone.utc)
        return (type_and_perms[0] == "-",
                type_and_perms[0] == "d",
                int(size),
                date_time,
                filename
                )

    def get_md5_sum(self) -> str:
        return adbtools.md5_sum(self._path)

    def list_dir(self) -> list[PathInfo]:
        ls_output_list: list[str] = adbtools.ls_ll(self._path)
        ls_output_list = ls_output_list[1:]  # first output is total amount
        return [AdbPathInfo(self._path, ls_output) for ls_output in ls_output_list]
    
    def get_child(self, child) -> PathInfo:
        return AdbPathInfo(posixpath.join(self._path, child))
    
    


def get_path_info(path: str) -> PathInfo:
    if path.startswith(ADB_PATTERN):
        return AdbPathInfo(path.replace(ADB_PATTERN, "", 1))
    return LocalPathInfo(path)
