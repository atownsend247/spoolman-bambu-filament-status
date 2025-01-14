"""Utilities for grabbing config from environment variables."""

import logging

from spoolman_bambu.state_tracker.state import StateTracker

logger = logging.getLogger(__name__)

# Initialise state
state = StateTracker()


def get_current_state() -> StateTracker:
    return state
