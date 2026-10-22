"""Reactor type templates."""

from __future__ import annotations

from enum import Enum

from pydantic import Field, model_validator

from .common import (
    FcsimModel,
    Fraction,
    NonNegativeFloat,
    Placeholder,
    PositiveFloat,
    WeightPercent,
)


class Spectrum(str, Enum):
    THERMAL = "thermal"
    FAST = "fast"


class ReactorType(FcsimModel):
    """Editable reactor technology template.

    Exactly one of ``residence_time_y`` and ``n_batches`` is given; the other is
    derived. ``enrichment_wt`` (UOX) or ``pu_content_wt`` (MOX), in weight percent
    of HM, override the value of the referenced fuel and are always user-editable.
    """

    name: str = Field(min_length=1)
    spectrum: Spectrum
    fuel: str = Field(min_length=1, description="Name of a Fuel in the scenario")
    unit_power_mwe: PositiveFloat | Placeholder
    thermal_efficiency: Fraction | Placeholder
    load_factor: Fraction | Placeholder
    discharge_burnup_gwd_per_thm: PositiveFloat | Placeholder
    residence_time_y: PositiveFloat | Placeholder | None = None
    n_batches: PositiveFloat | Placeholder | None = None
    core_mass_thm: PositiveFloat | Placeholder | None = None
    initial_core_factor: Fraction | Placeholder
    lifetime_y: PositiveFloat | Placeholder | None = None
    enrichment_wt: WeightPercent | Placeholder | None = None
    pu_content_wt: WeightPercent | Placeholder | None = None
    tails_assay_wt: WeightPercent | Placeholder | None = None
    cooling_time_y: NonNegativeFloat | Placeholder
    leakage_reactivity: float | Placeholder

    @model_validator(mode="after")
    def _check_batches(self) -> ReactorType:
        if (self.residence_time_y is None) == (self.n_batches is None):
            raise ValueError(
                f"reactor {self.name!r}: give exactly one of residence_time_y and n_batches"
            )
        return self
