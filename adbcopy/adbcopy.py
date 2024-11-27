from pathinfo import PathInfo, get_path_info
from logging import Logger, getLogger
import pathtools

__logger = getLogger(__name__)


def copy(src_path: str, target_path: str):
    src: PathInfo = get_path_info(src_path)
    target: PathInfo = get_path_info(target_path)

    if not src.exists():
        raise ValueError(f"source path does not exist: {src.get_path()}")
    if not target.exists():
        __logger.info("creating target directory %s", target_path)
        pathtools.mkdir(target)
    if target.is_file():
        raise ValueError(f"target path is file: {src.get_path()}")

    if src.is_file():
        pathtools.copy(src_path, target_path)
    else:
        pass
