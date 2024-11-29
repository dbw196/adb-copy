from adbcopy.pathinfo import PathInfo, LocalPathInfo, AdbPathInfo
import shutil
from adbcopy import adbtools
import os


def copy(src: PathInfo, target: PathInfo):
    src_path = src.get_path()
    target_path = target.get_path()
    if type(src) is LocalPathInfo and type(target) is LocalPathInfo:
        shutil.copy2(src_path, target_path)
    elif type(src) is LocalPathInfo and type(target) is AdbPathInfo:
        adbtools.push(src_path, target_path)
    elif type(src) is AdbPathInfo and type(target) is LocalPathInfo:
        adbtools.pull(src_path, target_path)
    elif type(src) is AdbPathInfo and type(target) is AdbPathInfo:
        adbtools.copy(src_path, target_path)
    else:
        raise ValueError(f"Unknown combination. src: {
                         type(src)}, target: {type(target)}")


def remove(path_info: PathInfo):
    path = path_info.get_path()
    if type(path_info) is AdbPathInfo:
        adbtools.remove(path)
    else:
        if path_info.is_dir():
            shutil.rmtree(path)
        else:
            os.remove(path)


def mkdir(path_info: PathInfo):
    path = path_info.get_path()
    if type(path_info) is AdbPathInfo:
        adbtools.makedirs(path)
    else:
        os.makedirs(path)
