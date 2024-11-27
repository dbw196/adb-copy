from typing import Final
import subprocess
from subprocess import CompletedProcess

ADB_COMMAND: Final[str] = "adb"

SHELL_COMMAND = [ADB_COMMAND, "shell"]

LS_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "ls", "-ll"]

EXISTS_SUBCOMMAND_PATTERN = f"[ -e '%s' ]"

IS_FILE_SUBCOMMAND_PATTERN = f"[ -f '%s' ]"

IS_DIR_SUBCOMMAND_PATTERN = f"[ -d '%s' ]"

MD5_COMMAND: Final[list[str]] = [*SHELL_COMMAND, "md5sum"]


def __run_command_with_output(*args: str) -> str:
    result: CompletedProcess = subprocess.run(
        args, capture_output=True, check=True, text=True, encoding="utf-8")
    return result.stdout


def __run_file_command(subcommand: str, path: str) -> bool:
    return subprocess.run([*SHELL_COMMAND, subcommand % path]).returncode == 0


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
