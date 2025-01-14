"""Pydantic data models for typing the FastAPI request/responses."""

import logging

from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, PlainSerializer

logger = logging.getLogger(__name__)


def datetime_to_str(dt: datetime) -> str:
    """Convert a datetime object to a string."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


SpoolmanDateTime = Annotated[datetime, PlainSerializer(datetime_to_str)]


class Message(BaseModel):
    message: str = Field()


class PrinterInfo(BaseModel):
    # Don't include printer code in here, for safety sake
    id: int = Field(examples=["unique id"])
    printer_id: str = Field(examples=["X1PXXAXXXXXXXXX"])
    printer_ip: str = Field(examples=["192.168.0.1"])
    status: str = Field(examples=["connected"])
    ams_unit_count: Optional[int] = Field(examples=["2"])
    ams_active_spools_count: Optional[int] = Field(examples=["3"])
    last_mqtt_message: Optional[SpoolmanDateTime] = Field(examples=["null", "2025-01-09T16:17:12.081846Z"])
    last_mqtt_ams_message: Optional[SpoolmanDateTime] = Field(examples=["null", "2025-01-09T16:17:12.081846Z"])


class Info(BaseModel):
    version: str = Field(examples=["0.7.0"])
    debug_mode: bool = Field(examples=[False])
    automatic_backups: bool = Field(examples=[True])
    data_dir: str = Field(examples=["/home/app/.local/share/spoolman"])
    logs_dir: str = Field(examples=["/home/app/.local/share/spoolman"])
    backups_dir: str = Field(examples=["/home/app/.local/share/spoolman/backups"])
    spoolman_connected: str = Field(examples=[True])
    spoolman_last_status_check: Optional[SpoolmanDateTime] = Field(examples=["null", "2025-01-09T16:17:12.081846Z"])


class HealthCheck(BaseModel):
    status: str = Field(examples=["healthy"])


class PrinterConfig(BaseModel):
    printer_id: str = Field(examples=["X1PXXAXXXXXXXXX"])
    printer_ip: str = Field(examples=["192.168.0.1"])
    printer_code: str = Field(examples=["XXXXXXXX"])


class MultiColorDirection(Enum):
    """Enum for multi-color direction."""

    COAXIAL = "coaxial"
    LONGITUDINAL = "longitudinal"


class Vendor(BaseModel):
    id: int = Field(description="Unique internal ID of this vendor.")
    registered: SpoolmanDateTime = Field(description="When the vendor was registered in the database. UTC Timezone.")
    name: str = Field(max_length=64, description="Vendor name.", examples=["Polymaker"])
    comment: Optional[str] = Field(
        None,
        max_length=1024,
        description="Free text comment about this vendor.",
        examples=[""],
    )
    empty_spool_weight: Optional[float] = Field(
        None,
        ge=0,
        description="The empty spool weight, in grams.",
        examples=[140],
    )
    external_id: Optional[str] = Field(
        None,
        max_length=256,
        description=(
            "Set if this vendor comes from an external database. This contains the ID in the external database."
        ),
        examples=["eSun"],
    )
    extra: dict[str, str] = Field(
        description=(
            "Extra fields for this vendor. All values are JSON-encoded data. "
            "Query the /fields endpoint for more details about the fields."
        ),
    )


class Filament(BaseModel):
    id: int = Field(description="Unique internal ID of this filament type.")
    registered: SpoolmanDateTime = Field(description="When the filament was registered in the database. UTC Timezone.")
    name: Optional[str] = Field(
        None,
        max_length=64,
        description=(
            "Filament name, to distinguish this filament type among others from the same vendor."
            "Should contain its color for example."
        ),
        examples=["PolyTerra™ Charcoal Black"],
    )
    vendor: Optional[Vendor] = Field(None, description="The vendor of this filament type.")
    material: Optional[str] = Field(
        None,
        max_length=64,
        description="The material of this filament, e.g. PLA.",
        examples=["PLA"],
    )
    price: Optional[float] = Field(
        None,
        ge=0,
        description="The price of this filament in the system configured currency.",
        examples=[20.0],
    )
    density: float = Field(gt=0, description="The density of this filament in g/cm3.", examples=[1.24])
    diameter: float = Field(gt=0, description="The diameter of this filament in mm.", examples=[1.75])
    weight: Optional[float] = Field(
        None,
        gt=0,
        description="The weight of the filament in a full spool, in grams.",
        examples=[1000],
    )
    spool_weight: Optional[float] = Field(None, ge=0, description="The empty spool weight, in grams.", examples=[140])
    article_number: Optional[str] = Field(
        None,
        max_length=64,
        description="Vendor article number, e.g. EAN, QR code, etc.",
        examples=["PM70820"],
    )
    comment: Optional[str] = Field(
        None,
        max_length=1024,
        description="Free text comment about this filament type.",
        examples=[""],
    )
    settings_extruder_temp: Optional[int] = Field(
        None,
        ge=0,
        description="Overridden extruder temperature, in °C.",
        examples=[210],
    )
    settings_bed_temp: Optional[int] = Field(
        None,
        ge=0,
        description="Overridden bed temperature, in °C.",
        examples=[60],
    )
    color_hex: Optional[str] = Field(
        None,
        min_length=6,
        max_length=8,
        description=(
            "Hexadecimal color code of the filament, e.g. FF0000 for red. Supports alpha channel at the end. "
            "If it's a multi-color filament, the multi_color_hexes field is used instead."
        ),
        examples=["FF0000"],
    )
    multi_color_hexes: Optional[str] = Field(
        None,
        min_length=6,
        description=(
            "Hexadecimal color code of the filament, e.g. FF0000 for red. Supports alpha channel at the end. "
            "Specifying multiple colors separated by commas. "
            "Also set the multi_color_direction field if you specify multiple colors."
        ),
        examples=["FF0000,00FF00,0000FF"],
    )
    multi_color_direction: Optional[MultiColorDirection] = Field(
        None,
        description=("Type of multi-color filament. Only set if the multi_color_hexes field is set."),
        examples=["coaxial", "longitudinal"],
    )
    external_id: Optional[str] = Field(
        None,
        max_length=256,
        description=(
            "Set if this filament comes from an external database. This contains the ID in the external database."
        ),
        examples=["polymaker_pla_polysonicblack_1000_175"],
    )
    extra: dict[str, str] = Field(
        description=(
            "Extra fields for this filament. All values are JSON-encoded data. "
            "Query the /fields endpoint for more details about the fields."
        ),
    )


class Spool(BaseModel):
    id: int = Field(description="Unique internal ID of this spool of filament.")
    registered: SpoolmanDateTime = Field(description="When the spool was registered in the database. UTC Timezone.")
    first_used: Optional[SpoolmanDateTime] = Field(
        None,
        description="First logged occurence of spool usage. UTC Timezone.",
    )
    last_used: Optional[SpoolmanDateTime] = Field(
        None,
        description="Last logged occurence of spool usage. UTC Timezone.",
    )
    filament: Filament = Field(description="The filament type of this spool.")
    price: Optional[float] = Field(
        None,
        ge=0,
        description="The price of this spool in the system configured currency.",
        examples=[20.0],
    )
    remaining_weight: Optional[float] = Field(
        default=None,
        ge=0,
        description=(
            "Estimated remaining weight of filament on the spool in grams. "
            "Only set if the filament type has a weight set."
        ),
        examples=[500.6],
    )
    initial_weight: Optional[float] = Field(
        default=None,
        ge=0,
        description=("The initial weight, in grams, of the filament on the spool (net weight)."),
        examples=[1246],
    )
    spool_weight: Optional[float] = Field(
        default=None,
        ge=0,
        description=("Weight of an empty spool (tare weight)."),
        examples=[246],
    )
    used_weight: float = Field(
        ge=0,
        description="Consumed weight of filament from the spool in grams.",
        examples=[500.3],
    )
    remaining_length: Optional[float] = Field(
        default=None,
        ge=0,
        description=(
            "Estimated remaining length of filament on the spool in millimeters."
            " Only set if the filament type has a weight set."
        ),
        examples=[5612.4],
    )
    used_length: float = Field(
        ge=0,
        description="Consumed length of filament from the spool in millimeters.",
        examples=[50.7],
    )
    location: Optional[str] = Field(
        None,
        max_length=64,
        description="Where this spool can be found.",
        examples=["Shelf A"],
    )
    lot_nr: Optional[str] = Field(
        None,
        max_length=64,
        description="Vendor manufacturing lot/batch number of the spool.",
        examples=["52342"],
    )
    comment: Optional[str] = Field(
        None,
        max_length=1024,
        description="Free text comment about this specific spool.",
        examples=[""],
    )
    archived: bool = Field(description="Whether this spool is archived and should not be used anymore.")
    extra: dict[str, str] = Field(
        description=(
            "Extra fields for this spool. All values are JSON-encoded data. "
            "Query the /fields endpoint for more details about the fields."
        ),
    )


class EventType(str, Enum):
    """Event types."""

    ADDED = "added"
    UPDATED = "updated"
    DELETED = "deleted"


class Event(BaseModel):
    """Event."""

    type: EventType = Field(description="Event type.")
    resource: str = Field(description="Resource type.")
    date: SpoolmanDateTime = Field(description="When the event occured. UTC Timezone.")
    payload: BaseModel
