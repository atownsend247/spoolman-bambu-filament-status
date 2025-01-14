import os
import pytest
import logging

from spoolman_bambu.bambu.ams_processor import calculate_spool_remaining_weight

# Set Logging
logging.basicConfig(level=logging.BASIC_FORMAT)

def test_calculate_weight_full() -> None:
    """
    Test calculate_spool_remaining_weight function
    :return: None
    """
    response = calculate_spool_remaining_weight(1000, 100)
    assert response == 1000.0

def test_calculate_weight_25() -> None:
    """
    Test calculate_spool_remaining_weight function
    :return: None
    """
    response = calculate_spool_remaining_weight(1000, 25)
    assert response == 250.0

