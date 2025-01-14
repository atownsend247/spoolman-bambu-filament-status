import logging
import asyncio

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from spoolman_bambu import env, state
from spoolman_bambu.api.v1.models import PrinterInfo
from spoolman_bambu.ws import websocket_manager


logger = logging.getLogger(__name__)
app_state = state.get_current_state()

router = APIRouter(
    prefix="/printer",
    tags=["printer"],
)


@router.get(
    "",
    name="Find printers",
    description=("Get a list of active printers"),
    response_model_exclude_none=True,
    responses={
        200: {"Printers": PrinterInfo},
    },
)
async def printer() -> JSONResponse:
    """Return general info about the API and statuses."""
    active_printers = []
    printers = app_state.get_printers()
    for index, printer in enumerate(printers):
        active_printers.append(get_printer_info(index + 1, printer))

    # Set x-total-count header for pagination
    return JSONResponse(
        content=jsonable_encoder(
            (active_printers),
        ),
        headers={"x-total-count": str(len(active_printers))},
    )


@router.websocket(
    "",
    name="Listen to printer changes",
)
async def notify_any(
    websocket: WebSocket,
) -> None:
    await websocket.accept()
    websocket_manager.connect(("printer",), websocket)
    try:
        while True:
            await asyncio.sleep(0.5)
            if await websocket.receive_text():
                await websocket.send_json({"status": "healthy"})
    except WebSocketDisconnect:
        websocket_manager.disconnect(("printer",), websocket)


@router.get(
    "/{printer_id}",
    name="Get printer",
    description=(
        "Get a specific filament. A websocket is served on the same path to listen for changes to the filament. "
        "See the HTTP Response code 299 for the content of the websocket messages."
    ),
    response_model_exclude_none=True,
    responses={404: {"model": PrinterInfo}},
)
async def get(
    printer_id: int,
) -> PrinterInfo:
    active_printer = None
    printers = app_state.get_printers()
    for index, printer in enumerate(printers):
        if index == (printer_id - 1):
            active_printer = get_printer_info(index + 1, printer)

    if active_printer is not None:
        return active_printer


@router.websocket(
    "/{printer_id}",
    name="Listen to spool changes",
)
async def notify(
    websocket: WebSocket,
    printer_id: int,
) -> None:
    await websocket.accept()
    websocket_manager.connect(("printer", str(printer_id)), websocket)
    try:
        while True:
            await asyncio.sleep(0.5)
            if await websocket.receive_text():
                await websocket.send_json({"status": "healthy"})
    except WebSocketDisconnect:
        websocket_manager.disconnect(("printer", str(printer_id)), websocket)


def get_printer_info(index, printer) -> PrinterInfo:
    return PrinterInfo(
        id=(index + 1),
        printer_ip=printer.get_printer_ip(),
        printer_id=printer.get_printer_id(),
        status=printer.get_status(),
        ams_unit_count=printer.get_ams_unit_count(),
        last_mqtt_message=printer.get_last_mqtt_message(),
        last_mqtt_ams_message=printer.get_last_mqtt_ams_message(),
    )
