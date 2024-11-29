from typing import Final
import subprocess
from subprocess import CompletedProcess

from logging import Logger, getLogger

__logger: Logger = getLogger(__name__)

ADB_COMMAND: Final[str] = "adb"

SHELL_COMMAND: Final[list[str]] = [ADB_COMMAND, "shell"]

PUSH_COMMAND: Final[list[str]] = [ADB_COMMAND, "push"]

PULL_COMMAND: Final[list[str]] = [ADB_COMMAND, "pull"]

LS_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "ls", "-llL"]

EXISTS_SUBCOMMAND_PATTERN: Final[str] = f"[ -e %s ]"

IS_FILE_SUBCOMMAND_PATTERN: Final[str] = f"[ -f %s ]"

IS_DIR_SUBCOMMAND_PATTERN: Final[str] = f"[ -d %s ]"

MD5_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "md5sum"]

MKDIR_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "mkdir", "-p"]

RM_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "rm", "-rf"]

CP_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "cp"]


def __run_command_with_output(*args: str) -> str:
    __logger.debug("__run_command_with_output: %s", " ".join(args))
    result: CompletedProcess = subprocess.run(
        args, capture_output=True, check=True, text=True, encoding="utf-8")
    return result.stdout


def __run_file_command(subcommand: str, path: str) -> bool:
    command = [*SHELL_COMMAND, subcommand % path]
    __logger.debug("__run_file_command: %s", " ".join(command))
    return subprocess.run(command).returncode == 0


def __run_command(*args: str) -> None:
    __logger.debug("__run_command: %s", " ".join(args))
    subprocess.run(
        args, check=True, text=True, encoding="utf-8")


def exists(path: str) -> bool:
    return __run_file_command(EXISTS_SUBCOMMAND_PATTERN, __escape(path))


def is_file(path: str) -> bool:
    return __run_file_command(IS_FILE_SUBCOMMAND_PATTERN, __escape(path))


def is_dir(path: str) -> bool:
    return __run_file_command(IS_DIR_SUBCOMMAND_PATTERN, __escape(path))


def ls_ll(path: str) -> list[str]:
    output: str = __run_command_with_output(*LS_COMMAND, __escape(path))
    lines: list[str] = output.strip().split("\n")
    return lines


def md5_sum(path: str) -> str:
    output: str = __run_command_with_output(*MD5_COMMAND, __escape(path))
    return output.split()[0]


def push(source_path: str, target_path: str):
    __run_command(*PUSH_COMMAND, source_path, target_path)


def pull(source_path: str, target_path: str):
    __run_command(*PULL_COMMAND, source_path, target_path)


def makedirs(path: str):
    __run_command(*MKDIR_COMMAND, __escape(path))


def remove(path: str):
    __run_command(*RM_COMMAND, __escape(path))


def copy(source_path: str, target_path: str):
    __run_command(*CP_COMMAND, __escape(source_path), __escape(target_path))

def __escape(path: str):
    # https://stackoverflow.com/a/31371987
    result = (path.replace(" ", r"\ ")
              .replace("'", r"\'")
              .replace("(", r"\(")
              .replace(")", r"\)")
              .replace("<", r"\<")
              .replace(">", r"\>")
              .replace(";", r"\;")
              .replace("&", r"\&")
              .replace("*", r"\*")
              .replace("~", r"\~")
              .replace("`", r"\`")
              .replace("%", r"\%")
              .replace("$", r"\$")
              )
    __logger.debug(result)
    return result
