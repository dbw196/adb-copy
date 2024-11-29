from adbcopy.pathinfo import PathInfo, get_path_info, ADB_PATTERN
from logging import Logger, getLogger
import logging
from adbcopy import pathtools
import argparse

__logger: Logger = getLogger(__name__)



def sync(src_path: str | PathInfo, target_path: str | PathInfo, check_md5_sum: bool = False) -> None:
    src: PathInfo = src_path if isinstance(src_path, PathInfo) else get_path_info(src_path)
    target: PathInfo = target_path if isinstance(target_path, PathInfo) else  get_path_info(target_path)
    if not src.exists():
        raise ValueError(f"source path does not exist: {src.get_path()}")
    if src.is_file():
        raise ValueError(f"source path is file: {src.get_path()}")
    if target.is_file():
        raise ValueError(f"target path is file: {target.get_path()}")
    if not target.exists():
        __logger.info("creating target directory %s", target.get_path())
        pathtools.mkdir(target)
    src_items: dict[str, PathInfo] = { path_info.get_name(): path_info for path_info in src.list_dir()}
    target_items: dict[str, PathInfo] = {path_info.get_name(): path_info for path_info in target.list_dir()}

    all_items: set[str] = src_items.keys() | target_items.keys()
    for name in sorted(all_items):
        if not name in src_items:
            __logger.info(f"deleting item in target: {target_items[name].get_path()}")
            pathtools.remove(target_items[name])
        else:
            src_item = src_items[name]
            if src_item.is_dir():
                if name in target_items and target_items[name].is_file():
                    target_item: PathInfo = target_items[name]
                    __logger.info(f"deleting file in target because it's dir in source: {target_item.get_path()}")
                    pathtools.remove(target_item)
                new_target: PathInfo = target.get_child(name)
                __logger.info(f"recursing into: {src_item.get_path()}")
                sync(src_item, new_target, check_md5_sum)
            elif not name in target_items:
                __logger.info(f"copying '{src_item.get_path()}' to '{target.get_path()}'")
                pathtools.copy(src_item, target)
            elif should_update(src_item, target_items[name], check_md5_sum): 
                target_item = target_items[name]
                __logger.info(f"updating '{target_item.get_path()}' with '{src_item.get_path()}'")
                pathtools.remove(target_item)
                pathtools.copy(src_item, target)
            else:
                __logger.info(f"keeping '{target_items[name].get_path()}'")

            
    #for src_item in src_items:
    #    if not src_item.get_name() in target_names:

def should_update(src: PathInfo, target: PathInfo, check_md5_sum: bool) -> bool:
    if not src.is_file():
        raise ValueError("src is not file")
    if not target.is_file():
        raise ValueError("target is not file")
    src_size = src.get_size()
    target_size = target.get_size()
    if src_size != target_size:
        __logger.info(f"size is different: {src_size} vs. {target_size}")
        return True
    src_modification_time = src.get_modification_time()
    target_modification_time = target.get_modification_time()
    if src_modification_time != target_modification_time:
        __logger.info(f"modification time is different: {src_modification_time} vs. {target_modification_time}")
        return True
    if check_md5_sum:
        src_md5_sum = src.get_md5_sum()
        target_md5_sum = target.get_md5_sum()
        if src_md5_sum != target_md5_sum:
            __logger.info(f"md5sum is different: {src_md5_sum} vs. {target_md5_sum}")
            return True
    return False


def main():
    
    description = """
Synchronizes two folders (one-way sync, target will mirror source).
For path arguments: If path begins with '%s', it is considered as a path on the device connected via ADB,
if not it is considered to be a local path.
"""%ADB_PATTERN
    
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument("src_path", help="The source path")
    arg_parser.add_argument("target_path", help="The target path")
    arg_parser.add_argument("--check_md5_sum", action="store_true", help="perform an md5 sum check in addition to modification time check when checking whether a file should be updated")
    arg_parser.add_argument("--verbose", action="store_true", help="enable verbose logging")

    args = arg_parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(asctime)s\t%(levelname)s\t%(filename)s\t\t%(message)s")

    sync(args.src_path, args.target_path, args.check_md5_sum)

if __name__ == "__main__":
    main()


