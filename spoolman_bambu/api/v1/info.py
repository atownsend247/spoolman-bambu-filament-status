import logging

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from spoolman_bambu import env, state
from spoolman_bambu.api.v1.models import Info

# from spoolman.extra_fields import EntityType, get_extra_fields, validate_extra_field_dict

logger = logging.getLogger(__name__)
app_state = state.get_current_state()

router = APIRouter(
    prefix="/info",
    tags=["info"],
)


@router.get(
    "",
    name="Get app info",
    description=("."),
    response_model_exclude_none=True,
    responses={
        200: {"Info": Info},
    },
)
async def info() -> Info:
    """Return general info about the API and statuses."""
    return Info(
        version=env.get_version(),
        debug_mode=env.is_debug_mode(),
        automatic_backups=env.is_automatic_backup_enabled(),
        spoolman_connected=app_state.get_spoolman().get_status(),
        spoolman_last_status_check=app_state.get_spoolman().get_last_status_check(),
        data_dir=str(env.get_data_dir().resolve()),
        logs_dir=str(env.get_logs_dir().resolve()),
        backups_dir=str(env.get_backups_dir().resolve()),
    )
