import logging
import datetime
import os

from scheduler.asyncio.scheduler import Scheduler

from spoolman_bambu import state

logger = logging.getLogger(__name__)

DEFAULT_SYNC_INTERVAL = 3600

app_state = state.get_current_state()

# TODO: Move this to env class
def get_spoolman_sync_interval() -> int:
    """Get the external database sync interval from environment variables. Defaults to DEFAULT_SYNC_INTERVAL."""
    return int(os.getenv("SPOOLMAN_BAMBU_SPOOLMAN_HEALTHCHECK_INTERVAL", DEFAULT_SYNC_INTERVAL))

async def _sync_spoolman() -> None:
    logger.info("Task: Syncing Spoolman health check connection...")

    app_state.get_spoolman().check_health()

    # filaments = _parse_filaments_from_bytes(await _download_file(url + "filaments.json"))
    # materials = _parse_materials_from_bytes(await _download_file(url + "materials.json"))

    # _write_to_local_cache("filaments.json", filaments.json().encode())
    # _write_to_local_cache("materials.json", materials.json().encode())

    logger.info(
        "Task: Spoolman health check connection synced"
    )

def spoolman_schedule_tasks(scheduler: Scheduler) -> None:
    """Schedule tasks to be executed by the provided scheduler.

    Args:
        scheduler: The scheduler to use for scheduling tasks.

    """
    schedule_interval = get_spoolman_sync_interval()
    logger.info(f"Task: Scheduling Spoolman health check every {schedule_interval} seconds.")

    # Run once on startup
    scheduler.once(datetime.timedelta(seconds=0), _sync_spoolman)  # type: ignore[arg-type]

    sync_interval = schedule_interval
    if sync_interval > 0:
        scheduler.cyclic(datetime.timedelta(seconds=sync_interval), _sync_spoolman)  # type: ignore[arg-type]
    else:
        logger.info("Task: Sync interval is 0, skipping periodic sync of Spoolman health.")

def printer_schedule_tasks(scheduler: Scheduler) -> None:
    """Schedule tasks to be executed by the provided scheduler.

    Args:
        scheduler: The scheduler to use for scheduling tasks.

    """