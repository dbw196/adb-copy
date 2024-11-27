from typing import Final
import subprocess
from subprocess import CompletedProcess

ADB_COMMAND: Final[str] = "adb"

SHELL_COMMAND: Final[list[str]] = [ADB_COMMAND, "shell"]

PUSH_COMMAND: Final[list[str]] = [ADB_COMMAND, "push"]

PULL_COMMAND: Final[list[str]] = [ADB_COMMAND, "pull"]

LS_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "ls", "-ll"]

EXISTS_SUBCOMMAND_PATTERN: Final[str] = f"[ -e '%s' ]"

IS_FILE_SUBCOMMAND_PATTERN: Final[str] = f"[ -f '%s' ]"

IS_DIR_SUBCOMMAND_PATTERN: Final[str] = f"[ -d '%s' ]"

MD5_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "md5sum"]

MKDIR_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "mkdir"]

RM_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "rm"]

CP_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "cp"]


def __run_command_with_output(*args: str) -> str:
    result: CompletedProcess = subprocess.run(
        args, capture_output=True, check=True, text=True, encoding="utf-8")
    return result.stdout


def __run_file_command(subcommand: str, path: str) -> bool:
    return subprocess.run([*SHELL_COMMAND, subcommand % path]).returncode == 0


def __run_command(*args: str) -> None:
    subprocess.run(
        args, check=True, text=True, encoding="utf-8")


def exists(path: str) -> bool:
    return __run_file_command(EXISTS_SUBCOMMAND_PATTERN, path)


def is_file(path: str) -> bool:
    return __run_file_command(IS_FILE_SUBCOMMAND_PATTERN, path)


def is_dir(path: str) -> bool:
    return __run_file_command(IS_DIR_SUBCOMMAND_PATTERN, path)


def ls_ll(path: str) -> list[str]:
    output: str = __run_command_with_output(*LS_COMMAND, f"'{path}'")
    lines: list[str] = output.strip().split("\n")
    return lines


def md5_sum(path: str) -> str:
    output: str = __run_command_with_output(*MD5_COMMAND, f"'{path}'")
    return output.split()[0]


def push(source_path: str, target_path: str):
    __run_command(*PUSH_COMMAND, f"'{source_path}'", f"'{target_path}'")


def pull(source_path: str, target_path: str):
    __run_command(*PULL_COMMAND, f"'{source_path}'", f"'{target_path}'")


def mkdir(path: str):
    __run_command(*MKDIR_COMMAND, f"'{path}'")


def remove(path: str):
    __run_command(*RM_COMMAND, f"'{path}'")


def copy(source_path: str, target_path: str):
    __run_command(*CP_COMMAND, f"'{source_path}'", f"'{target_path}'")
