"""handles the app state."""

import logging

logger = logging.getLogger(__name__)


class StateTracker:
    def __init__(self):
        """
        Initializes the URLHealthChecker instance.

        """

        self._spoolman = None
        self._printers = []
        self._spools = None

        logger.info(
            "State instance configured"
        )

    def set_spoolman(self, spoolman):
        self._spoolman = spoolman

    
    def get_spoolman(self):
        if self._spoolman is None:
            logger.warning(
                "Spoolman state is not initialised"
            )
        else:
            return self._spoolman

    def add_printer(self, printer):
        # Check if already exists, if so update, else append
        if printer in self._printers:
            for i, item in enumerate(self._printers):
                if item == printer:
                    mylist[i] = printer
        else: 
            self._printers.append(printer)
    
    def get_printers(self):
        return self._printers

    def set_spoolman_spools(self, spools):
        self._spools = spools

    def get_spoolman_spools(self):
        if self._spools is None:
            logger.warning(
                "Spoolman Spools state is not initialised"
            )
        else:
            return self._spools