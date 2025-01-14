import os
import pytest
import logging

from spoolman_bambu.task_scheduler import get_spoolman_sync_interval

# Set Logging
logging.basicConfig(level=logging.BASIC_FORMAT)

def test_get_spoolman_sync_interval_default() -> None:
    """
    Test get_spoolman_sync_interval function with default
    :return: None
    """
    response = get_spoolman_sync_interval()
    assert response == 600

def test_get_spoolman_sync_interval_env_var() -> None:
    """
    Test get_spoolman_sync_interval function with env var[SPOOLMAN_BAMBU_SPOOLMAN_HEALTHCHECK_INTERVAL] set
    :return: None
    """
    os.environ["SPOOLMAN_BAMBU_SPOOLMAN_HEALTHCHECK_INTERVAL"] = "1200"
    response = get_spoolman_sync_interval()
    assert response == 1200
