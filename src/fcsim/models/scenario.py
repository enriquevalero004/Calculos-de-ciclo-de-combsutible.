"""Scenario: the complete, serialisable input of a simulation."""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from .common import FcsimModel, NonNegativeFloat, find_placeholders, validate_composition
from .cycle import CycleOptions
from .fleet import Fleet
from .fuel import Fuel, FuelKind
from .reactor import ReactorType

SCHEMA_VERSION = 1
MAX_END_YEAR = 2200


class InitialStocks(FcsimModel):
    """Material stocks at ``start_year``.

    Attributes:
        separated_pu_t: separated Pu (t) with isotopic mass fractions ``pu_vector``.
        spent_fuel_thm: spent fuel (tHM) with optional composition per nuclide.
        depleted_u_t: depleted uranium (t).
    """

    separated_pu_t: NonNegativeFloat = 0.0
    pu_vector: dict[str, float] | None = None
    spent_fuel_thm: NonNegativeFloat = 0.0
    spent_fuel_composition: dict[str, float] | None = None
    depleted_u_t: NonNegativeFloat = 0.0

    @field_validator("pu_vector", "spent_fuel_composition")
    @classmethod
    def _check_vectors(cls, value: dict[str, float] | None, info) -> dict[str, float] | None:
        return None if value is None else validate_composition(value, info.field_name)

    @model_validator(mode="after")
    def _pu_needs_vector(self) -> InitialStocks:
        if self.separated_pu_t > 0 and self.pu_vector is None:
            raise ValueError("initial separated Pu needs a pu_vector")
        return self


class Scenario(FcsimModel):
    schema_version: int = SCHEMA_VERSION
    name: str = Field(min_length=1)
    description: str = ""
    start_year: int
    end_year: int = Field(le=MAX_END_YEAR)
    fuels: list[Fuel] = Field(default_factory=list)
    reactor_types: list[ReactorType] = Field(default_factory=list)
    fleets: list[Fleet] = Field(default_factory=list)
    cycle: CycleOptions = Field(default_factory=CycleOptions)
    initial_stocks: InitialStocks = Field(default_factory=InitialStocks)

    @model_validator(mode="after")
    def _check_consistency(self) -> Scenario:
        if self.end_year <= self.start_year:
            raise ValueError("end_year must be after start_year")
        fuels = _unique(self.fuels, "fuel")
        reactors = _unique(self.reactor_types, "reactor type")
        fleets = _unique(self.fleets, "fleet")

        for r in self.reactor_types:
            if r.fuel not in fuels:
                raise ValueError(f"reactor type {r.name!r} references unknown fuel {r.fuel!r}")
            kind = fuels[r.fuel].kind
            if kind is not FuelKind.UOX and r.enrichment_wt is not None:
                raise ValueError(f"reactor type {r.name!r}: enrichment_wt only applies to UOX fuel")
            if kind is not FuelKind.MOX and r.pu_content_wt is not None:
                raise ValueError(f"reactor type {r.name!r}: pu_content_wt only applies to MOX fuel")

        for f in self.fleets:
            if f.reactor_type not in reactors:
                raise ValueError(f"fleet {f.name!r} references unknown reactor type {f.reactor_type!r}")
            for ref in (f.replaces, f.linked_to.fleet if f.linked_to else None):
                if ref is not None and ref not in fleets:
                    raise ValueError(f"fleet {f.name!r} references unknown fleet {ref!r}")
                if ref == f.name:
                    raise ValueError(f"fleet {f.name!r} cannot reference itself")

        for label, names in (
            ("reprocessed_fraction", self.cycle.reprocessed_fraction),
            ("delays.cooling_y", self.cycle.delays.cooling_y),
        ):
            unknown = sorted(set(names) - set(fleets))
            if unknown:
                raise ValueError(f"cycle.{label} references unknown fleets {unknown}")
        return self

    def placeholders(self) -> list[str]:
        """Dotted paths of every value still marked PLACEHOLDER."""
        return find_placeholders(self)


def _unique(items: list, label: str) -> dict:
    by_name: dict = {}
    for item in items:
        if item.name in by_name:
            raise ValueError(f"duplicate {label} name {item.name!r}")
        by_name[item.name] = item
    return by_name
