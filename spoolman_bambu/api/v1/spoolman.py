import logging

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from spoolman_bambu import env, state
from spoolman_bambu.api.v1.models import Spool

# from spoolman.extra_fields import EntityType, get_extra_fields, validate_extra_field_dict

logger = logging.getLogger(__name__)
app_state = state.get_current_state()

router = APIRouter(
    prefix="/spoolman",
    tags=["spoolman"],
)


@router.get(
    "/spools",
    name="Find spool",
    description=(
        "Get a list of spools that matches the search query. "
        "A websocket is served on the same path to listen for updates to any spool, or added or deleted spools. "
        "See the HTTP Response code 299 for the content of the websocket messages."
    ),
    response_model_exclude_none=True,
    responses={
        200: {"model": list[Spool]},
    },
)
def find() -> JSONResponse:
    spoolman_spools = app_state.get_spoolman_spools()
    logger.info(f"Pre response: {spoolman_spools}")
    # Set x-total-count header for pagination
    return JSONResponse(
        content=jsonable_encoder(
            (spoolman_spools),
            exclude_none=True,
        ),
    )
