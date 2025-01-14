"""Utilities for grabbing config from environment variables."""

import logging
import os
import subprocess
import sys
import json

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib import parse

from platformdirs import user_data_dir
from pydantic import ValidationError

from spoolman_bambu.api.v1.models import PrinterConfig

logger = logging.getLogger(__name__)


def get_logging_level() -> int:
    """Get the logging level from environment variables.

    Returns "INFO" if no environment variable was set for the logging level.

    Returns:
        str: The logging level.

    """
    log_level_str = os.getenv("SPOOLMAN_BAMBU_LOGGING_LEVEL", "INFO").upper()
    if log_level_str == "DEBUG":
        return logging.DEBUG
    if log_level_str == "INFO":
        return logging.INFO
    if log_level_str == "WARNING":
        return logging.WARNING
    if log_level_str == "ERROR":
        return logging.ERROR
    if log_level_str == "CRITICAL":
        return logging.CRITICAL
    raise ValueError(f"Failed to parse SPOOLMAN_BAMBU_LOGGING_LEVEL variable: Unknown logging level '{log_level_str}'.")


def is_debug_mode() -> bool:
    """Get whether debug mode is enabled from environment variables.

    Returns False if no environment variable was set for debug mode.

    Returns:
        bool: Whether debug mode is enabled.

    """
    debug_mode = os.getenv("SPOOLMAN_BAMBU_DEBUG_MODE", "FALSE").upper()
    if debug_mode in {"FALSE", "0"}:
        return False
    if debug_mode in {"TRUE", "1"}:
        return True
    raise ValueError(f"Failed to parse SPOOLMAN_BAMBU_DEBUG_MODE variable: Unknown debug mode '{debug_mode}'.")


def is_automatic_backup_enabled() -> bool:
    """Get whether automatic backup is enabled from environment variables.

    Returns True if no environment variable was set for automatic backup.

    Returns:
        bool: Whether automatic backup is enabled.

    """
    automatic_backup = os.getenv("SPOOLMAN_BAMBU_AUTOMATIC_BACKUP", "TRUE").upper()
    if automatic_backup in {"FALSE", "0"}:
        return False
    if automatic_backup in {"TRUE", "1"}:
        return True
    raise ValueError(
        f"Failed to parse SPOOLMAN_BAMBU_AUTOMATIC_BACKUP variable: Unknown automatic backup '{automatic_backup}'.",
    )


def get_data_dir() -> Path:
    """Get the data directory.

    Returns:
        Path: The data directory.

    """
    env_data_dir = os.getenv("SPOOLMAN_BAMBU_DIR_DATA")
    if env_data_dir is not None:
        data_dir = Path(env_data_dir)
    else:
        data_dir = Path(user_data_dir("spoolman_bambu"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_logs_dir() -> Path:
    """Get the logs directory.

    Returns:
        Path: The logs directory.

    """
    env_logs_dir = os.getenv("SPOOLMAN_BAMBU_DIR_LOGS")
    if env_logs_dir is not None:
        logs_dir = Path(env_logs_dir)
    else:
        logs_dir = get_data_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_spoolman_bambu_host() -> str:
    env_spoolman_ip = os.getenv("SPOOLMAN_BAMBU_HOST")
    if env_spoolman_ip is not None:
        return env_spoolman_ip
    raise ValueError(
        f"Failed to parse SPOOLMAN_BAMBU_HOST variable: Unknown automatic backup '{env_spoolman_ip}'.",
    )


def get_spoolman_bambu_port() -> str:
    env_spoolman_port = os.getenv("SPOOLMAN_BAMBU_PORT")
    if env_spoolman_port is not None:
        return env_spoolman_port
    raise ValueError(
        f"Failed to parse SPOOLMAN_BAMBU_PORT variable: Unknown automatic backup '{env_spoolman_port}'.",
    )


def get_spoolman_ip() -> str:
    env_spoolman_ip = os.getenv("SPOOLMAN_BAMBU_SPOOLMAN_IP")
    if env_spoolman_ip is not None:
        return env_spoolman_ip
    raise ValueError(
        f"Failed to parse SPOOLMAN_BAMBU_SPOOLMAN_IP variable: Unknown automatic backup '{env_spoolman_ip}'.",
    )


def get_spoolman_port() -> str:
    env_spoolman_port = os.getenv("SPOOLMAN_BAMBU_SPOOLMAN_PORT")
    if env_spoolman_port is not None:
        return env_spoolman_port
    raise ValueError(
        f"Failed to parse SPOOLMAN_BAMBU_SPOOLMAN_PORT variable: Unknown automatic backup '{env_spoolman_port}'.",
    )


def get_spoolman_tag() -> str:
    env_spoolman_tag = os.getenv("SPOOLMAN_BAMBU_SPOOLMAN_TAG")
    if env_spoolman_tag is not None:
        return env_spoolman_tag
    else:
        # Return the default value
        return "Tag"


def get_backups_dir() -> Path:
    """Get the backups directory.

    Returns:
        Path: The backups directory.

    """
    env_backups_dir = os.getenv("SPOOLMAN_BAMBU_DIR_BACKUPS")
    if env_backups_dir is not None:
        backups_dir = Path(env_backups_dir)
    else:
        backups_dir = get_data_dir().joinpath("backups")
    backups_dir.mkdir(parents=True, exist_ok=True)
    return backups_dir


def get_cache_dir() -> Path:
    """Get the cache directory."""
    return get_data_dir() / "cache"


def get_version() -> str:
    """Get the version of the package.

    Returns:
        str: The version.

    """
    # Read version from pyproject.toml, don't use pkg_resources because it requires the package to be installed
    with Path("pyproject.toml").open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("version ="):
                return line.split('"')[1]
    return "unknown"


def get_commit_hash() -> Optional[str]:
    """Get the latest commit hash of the package.

    Can end with "-dirty" if there are uncommitted changes.

    Returns:
        Optional[str]: The commit hash.

    """
    # Read commit has from build.txt
    # commit is written as GIT_COMMIT=<hash> in build.txt
    build_file = Path("build.txt")
    if not build_file.exists():
        return None
    with build_file.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("GIT_COMMIT="):
                return line.split("=")[1].strip()
    return None


def get_build_date() -> Optional[datetime]:
    """Get the build date of the package.

    Returns:
        Optional[datetime.datetime]: The build date.

    """
    # Read build date has from build.txt
    # build date is written as BUILD_DATE=<hash> in build.txt
    build_file = Path("build.txt")
    if not build_file.exists():
        return None
    with build_file.open(encoding="utf-8") as f:
        for line in f:
            if line.startswith("BUILD_DATE="):
                try:
                    return datetime.fromisoformat(line.split("=")[1].strip())
                except ValueError:
                    return None
    return None


def can_write_to_data_dir() -> bool:
    """Check if the data directory is writable."""
    try:
        test_file = get_data_dir().joinpath("test.txt")
        test_file.touch()
        test_file.unlink()
    except:  # noqa: E722
        return False
    return True


def chown_dir(path: str) -> bool:
    """Try to chown the data directory to the current user."""
    if os.name == "nt":
        return False

    try:
        uid = os.getuid()
        gid = os.getgid()
        subprocess.run(["chown", "-R", f"{uid}:{gid}", path], check=True)  # noqa: S603, S607
    except:  # noqa: E722
        return False
    return True


def check_write_permissions() -> None:
    """Verify that the data directory is writable, crash with a helpful error message if not."""
    if not can_write_to_data_dir():
        # If windows we can't fix the permissions, so just crash
        if os.name == "nt":
            logger.error("Data directory is not writable.")
            sys.exit(1)

        # Try fixing it by chowning the directory to the current user
        logger.warning("Data directory is not writable, trying to fix it...")
        if not chown_dir(str(get_data_dir())) or not can_write_to_data_dir():
            uid = os.getuid()
            gid = os.getgid()

            logger.error(
                (
                    "Data directory is not writable. "
                    'Please run "sudo chown -R %s:%s /path/to/spoolman/datadir" on the host OS.'
                ),
                uid,
                gid,
            )
            sys.exit(1)


def is_docker() -> bool:
    """Check if we are running in a docker container."""
    return Path("/.dockerenv").exists()


def is_data_dir_mounted() -> bool:
    """Check if the data directory is mounted as a shfs."""
    # "mount" will give us a list of all mounted filesystems
    mounts = subprocess.run("mount", check=True, stdout=subprocess.PIPE, text=True)  # noqa: S603, S607
    data_dir = str(get_data_dir().resolve())
    return any(data_dir in line for line in mounts.stdout.splitlines())


def convert_id_to_char(id) -> str:
    # TODO: Make better
    if id == "0":
        return "A"
    elif id == "1":
        return "B"
    elif id == "2":
        return "C"
    elif id == "3":
        return "D"


def get_base_path() -> str:
    """Get the base path.

    This is formated so that it always starts with a /, and does not end with a /

    Returns:
        str: The base path.

    """
    path = os.getenv("SPOOLMAN_BAMBU_BASE_PATH", "")
    if len(path) == 0:
        return ""

    # Ensure it starts with / and does not end with /
    return "/" + path.strip("/")


def get_all_printer_env_vars() -> list[PrinterConfig]:
    prefix_check = "SPOOLMAN_BAMBU_PRINTER_"
    all_env_vars = os.environ.items()
    collected_vars = {}
    # Find all env vars prefixed with SPOOLMAN_BAMBU_PRINTER_
    # and append them to a dict by each printer
    for name, value in all_env_vars:
        if name.startswith(prefix_check):
            if name[0:24] not in collected_vars.keys():
                collected_vars[name[0:24]] = {}
            # Create array per printer to further process
            collected_vars[name[0:24]][name[25:].lower()] = value

    processed_list = []

    # Iterate over the refined dict and initialise them as PrinterConfig
    for index, printer_env in collected_vars.items():
        try:
            printer_config = PrinterConfig(
                printer_id=printer_env["id"], printer_ip=printer_env["ip"], printer_code=printer_env["code"]
            )
            processed_list.append(printer_config)
        except KeyError as e:
            logger.error(f"Failed configuring printer [{index}]:{e} is missing")
        except ValidationError as e:
            logger.error(f"Failed configuring printer [{index}]:{json.dumps(e.errors()[0])}")

    return processed_list
