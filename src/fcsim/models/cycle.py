"""Fuel cycle options: open/closed, losses, delays, reprocessing."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import Field

from .common import PLACEHOLDER, FcsimModel, Fraction, NonNegativeFloat, Placeholder


class CycleType(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class Losses(FcsimModel):
    """Process loss fractions (lost / input) per stage, all editable."""

    mining_milling: Fraction | Placeholder = PLACEHOLDER
    conversion: Fraction | Placeholder = PLACEHOLDER
    enrichment_process: Fraction | Placeholder = PLACEHOLDER  # besides the tails
    uox_fabrication: Fraction | Placeholder = PLACEHOLDER
    reprocessing_pu: Fraction | Placeholder = PLACEHOLDER
    reprocessing_u: Fraction | Placeholder = PLACEHOLDER
    mox_fabrication: Fraction | Placeholder = PLACEHOLDER


class Delays(FcsimModel):
    """Delays in years.

    Cooling time is taken from ``ReactorType.cooling_time_y``; ``cooling_y``
    overrides it per fleet name.
    """

    fabrication_lead_y: NonNegativeFloat | Placeholder = PLACEHOLDER
    reprocessing_y: NonNegativeFloat | Placeholder = PLACEHOLDER
    mox_fabrication_y: NonNegativeFloat | Placeholder = PLACEHOLDER
    cooling_y: dict[str, NonNegativeFloat] = Field(default_factory=dict)


class CycleOptions(FcsimModel):
    """Back-end and front-end options of the scenario.

    Attributes:
        reprocessed_fraction: {fleet name: fraction of cooled spent fuel reprocessed};
            fleets not listed reprocess 0.
        reprocessing_capacity_thm_per_y: "unlimited" or {year: tHM/y}.
        pu_reserve_t: minimum separated Pu stock (t) for the closed-cycle diagnostic.
        hlw_glass_factor: glass per tonne of FP + MA, in ``hlw_glass_unit``.
    """

    type: CycleType = CycleType.OPEN
    reprocessed_fraction: dict[str, Fraction] = Field(default_factory=dict)
    losses: Losses = Field(default_factory=Losses)
    delays: Delays = Field(default_factory=Delays)
    reprocessing_capacity_thm_per_y: Literal["unlimited"] | dict[int, NonNegativeFloat] = "unlimited"
    pu_reserve_t: NonNegativeFloat | Placeholder = PLACEHOLDER
    repU_recycling: bool = False
    hlw_glass_factor: NonNegativeFloat | Placeholder = PLACEHOLDER
    hlw_glass_unit: Literal["m3_per_t", "t_per_t"] = "m3_per_t"
