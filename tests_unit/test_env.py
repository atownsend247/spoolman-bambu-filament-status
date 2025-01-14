import os
import pytest
import logging

from spoolman_bambu.env import convert_id_to_char, get_logging_level

# Set Logging
logging.basicConfig(level=logging.BASIC_FORMAT)

def test_convert_id_to_char_0() -> None:
    """
    Test convert_id_to_char function with 0
    :return: None
    """
    response = convert_id_to_char("0")
    assert response == "A"

def test_convert_id_to_char_1() -> None:
    """
    Test convert_id_to_char function with 1
    :return: None
    """
    response = convert_id_to_char("1")
    assert response == "B"

def test_convert_id_to_char_2() -> None:
    """
    Test convert_id_to_char function with 2
    :return: None
    """
    response = convert_id_to_char("2")
    assert response == "C"

def test_convert_id_to_char() -> None:
    """
    Test convert_id_to_char function with 3
    :return: None
    """
    response = convert_id_to_char("3")
    assert response == "D"

def test_get_logging_level_default() -> None:
    response = get_logging_level()
    assert response == logging.INFO

def test_get_logging_level_info() -> None:
    os.environ["SPOOLMAN_BAMBU_LOGGING_LEVEL"] = "INFO"
    response = get_logging_level()
    assert response == logging.INFO

def test_get_logging_level_debug() -> None:
    os.environ["SPOOLMAN_BAMBU_LOGGING_LEVEL"] = "DEBUG"
    response = get_logging_level()
    assert response == logging.DEBUG

def test_get_logging_level_warning() -> None:
    os.environ["SPOOLMAN_BAMBU_LOGGING_LEVEL"] = "WARNING"
    response = get_logging_level()
    assert response == logging.WARNING

def test_get_logging_level_error() -> None:
    os.environ["SPOOLMAN_BAMBU_LOGGING_LEVEL"] = "ERROR"
    response = get_logging_level()
    assert response == logging.ERROR

def test_get_logging_level_critical() -> None:
    os.environ["SPOOLMAN_BAMBU_LOGGING_LEVEL"] = "CRITICAL"
    response = get_logging_level()
    assert response == logging.CRITICAL