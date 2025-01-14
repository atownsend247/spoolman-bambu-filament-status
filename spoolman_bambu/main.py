"""Main entrypoint to the server."""

import logging
import subprocess
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from scheduler.asyncio.scheduler import Scheduler

from spoolman_bambu import env, state, task_scheduler
from spoolman_bambu.spoolman.spoolman import Spoolman
from spoolman_bambu.bambu.bambu import Bambu
from spoolman_bambu.api.v1.router import app as v1_app
from spoolman_bambu.client.client import SinglePageApplication

# Define a console logger
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(name)-26s %(levelname)-8s %(message)s"))

# Setup the spoolman_bambu logger, which all spoolman_bambu modules will use
log_level = env.get_logging_level()
root_logger = logging.getLogger()
root_logger.setLevel(log_level)
root_logger.addHandler(console_handler)

# Fix uvicorn logging
logging.getLogger("uvicorn").setLevel(log_level)
logging.getLogger("uvicorn").removeHandler(logging.getLogger("uvicorn").handlers[0])
logging.getLogger("uvicorn").addHandler(console_handler)

logging.getLogger("uvicorn.error").setLevel(log_level)
logging.getLogger("uvicorn.error").addHandler(console_handler)

logging.getLogger("uvicorn.access").setLevel(log_level)
logging.getLogger("uvicorn.access").removeHandler(logging.getLogger("uvicorn.access").handlers[0])
logging.getLogger("uvicorn.access").addHandler(console_handler)

# Get logger instance for this module
logger = logging.getLogger(__name__)

app_state = state.get_current_state()

# Setup FastAPI
app = FastAPI(
    debug=env.is_debug_mode(),
    title="Spoolman Bambu",
    version=env.get_version(),
)
app.add_middleware(GZipMiddleware)
app.mount(env.get_base_path() + "/api/v1", v1_app)

base_path = env.get_base_path()
if base_path != "":
    logger.info("Base path is: %s", base_path)

    # If base path is set, add a redirect from non-slash suffix to slash
    # suffix. Otherwise it won't work.
    @app.get(base_path)
    def root_redirect() -> Response:
        """Redirect to base path."""
        return RedirectResponse(base_path + "/")


# Return a dynamic js config file
# This is so that the client side can access the base path variable.
@app.get(env.get_base_path() + "/config.js")
def get_configjs() -> Response:
    """Return a dynamic js config file."""
    if '"' in base_path:
        raise ValueError("Base path contains quotes, which are not allowed.")

    return Response(
        content=f"""
window.SPOOLMAN_BAMBU_BASE_PATH = "{base_path}";
""",
        media_type="text/javascript",
    )


# Mount the client side app
app.mount(base_path, app=SinglePageApplication(directory="client/dist", base_path=env.get_base_path()))

# Allow all origins if in debug mode
if env.is_debug_mode():
    logger.warning("Running in debug mode, allowing all origins.")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"],
    )


def add_file_logging() -> None:
    """Add file logging to the root logger."""
    # Define a file logger with log rotation
    log_file = env.get_logs_dir().joinpath("spoolman_bambu.log")
    file_handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=5)
    file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(message)s", "%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(file_handler)


def initialise_spoolman() -> None:
    """Initialise Spoolman connection and instance."""
    # Initialise spoolman
    spoolman = Spoolman()
    app_state.set_spoolman(spoolman)
    spoolman.check_health()
    spoolman.initialise()
    # Get the initial state of the spools
    app_state.set_spoolman_spools(spoolman.get_spools())


def initialise_printers() -> None:
    """Initialise printers connection and instance."""
    printers = env.get_all_printer_env_vars()
    logger.info(f"Found {len(printers)} printers in env configuration, initilising them now...")

    if len(printers) == 0:
        logger.warning("No printers configured via env variables, please see project readme...")

    for printer in printers:
        app_state.add_printer(Bambu(printer.printer_id, printer.printer_ip, printer.printer_code))
    logger.info(f"{len(printers)} printers initilised")


@app.on_event("startup")
async def startup() -> None:
    """Run the service's startup sequence."""

    # Don't add file logging until we have verified that the data directory is writable
    add_file_logging()

    logger.info(
        "Starting Spoolman Plugin Bambu Filiment Status v%s",
        app.version,
    )

    logger.info("Configuration:")
    logger.info("Using data directory: %s", env.get_data_dir().resolve())
    logger.info("Using logs directory: %s", env.get_logs_dir().resolve())
    logger.info("Using backups directory: %s", env.get_backups_dir().resolve())
    logger.info("")

    # Initialise state
    # Initialise spoolman
    initialise_spoolman()
    # Initialise printers
    initialise_printers()

    # Setup scheduler
    schedule = Scheduler()
    task_scheduler.spoolman_schedule_tasks(schedule)
    # externaldb.schedule_tasks(schedule)

    logger.info("Startup complete.")


@app.on_event("shutdown")
async def shutdown() -> None:
    """Run the service's shutdown sequence."""

    logger.info(
        "Shutting down Spoolman Plugin Bambu Filiment Status v%s",
        app.version,
    )

    active_printers = app_state.get_printers()
    for printer in active_printers:
        logger.info(f"Shutting down printer: {printer.get_printer_id()}...")
        if printer.get_status() == "connected":
            printer.disconnect()

    logger.info("Shutdown complete.")


if __name__ == "__main__":
    uvicorn.run(app, host=env.get_spoolman_bambu_host(), port=env.get_spoolman_bambu_port())
