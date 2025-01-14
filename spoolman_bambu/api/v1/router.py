"""Router setup for the v1 version of the API."""

# ruff: noqa: D103

import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import Response

from spoolman_bambu import env, state
from spoolman_bambu.exceptions import ItemNotFoundError

from . import info, models, printer, spoolman

logger = logging.getLogger(__name__)
app_state = state.get_current_state()

app = FastAPI(
    title="Spoolman Bambu REST API v1",
    version="1.0.0",
    description="""
    REST API for Spoolman Bambu Filiment Status.

    The API is served on the path `/api/v1/`.

    Some endpoints also serve a websocket on the same path. The websocket is used to listen for changes to the data
    that the endpoint serves. The websocket messages are JSON objects. Additionally, there is a root-level websocket
    endpoint that listens for changes to any data in the database.
    """,
)


@app.exception_handler(ItemNotFoundError)
async def itemnotfounderror_exception_handler(_request: Request, exc: ItemNotFoundError) -> Response:
    logger.debug(exc, exc_info=True)
    return JSONResponse(
        status_code=404,
        content={"message": exc.args[0]},
    )


# Add health check endpoint
@app.get("/health")
async def health() -> models.HealthCheck:
    """Return a health check."""
    return models.HealthCheck(status="healthy")


# Add routers
app.include_router(info.router)
app.include_router(printer.router)
app.include_router(spoolman.router)
