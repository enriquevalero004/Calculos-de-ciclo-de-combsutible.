"""Fuel definitions (UOX, MOX, CUSTOM)."""

from __future__ import annotations

from enum import Enum

from pydantic import Field, field_validator, model_validator

from .common import FcsimModel, Placeholder, WeightPercent, validate_composition


class FuelKind(str, Enum):
    UOX = "UOX"
    MOX = "MOX"
    CUSTOM = "CUSTOM"
    # v2: THORIUM, MA


class PuVectorSource(str, Enum):
    STOCK = "stock"  # isotopic vector of the separated Pu stock available that year
    FIXED = "fixed"  # isotopic vector given in ``pu_vector``


class UMatrix(str, Enum):
    DEPLETED = "depleted"
    NATURAL = "natural"
    REPU = "repU"


class Fuel(FcsimModel):
    """A fuel type.

    Attributes:
        composition: mass fractions per nuclide over heavy metal (HM); must sum to 1.
            Required for CUSTOM; for UOX and MOX it is derived by the physics modules.
        enrichment_wt: U-235 content of UOX, in weight percent of HM.
        pu_content_wt: total Pu over HM of MOX, in weight percent.
        pu_vector: Pu isotopic mass fractions (sum 1), required for MOX with
            ``pu_vector_source = fixed``.
    """

    name: str = Field(min_length=1)
    kind: FuelKind
    description: str = ""
    composition: dict[str, float] | None = None
    enrichment_wt: WeightPercent | Placeholder | None = None
    pu_content_wt: WeightPercent | Placeholder | None = None
    pu_vector_source: PuVectorSource | None = None
    pu_vector: dict[str, float] | None = None
    u_matrix: UMatrix | None = None

    @field_validator("composition")
    @classmethod
    def _check_composition(cls, value: dict[str, float] | None) -> dict[str, float] | None:
        return None if value is None else validate_composition(value, "composition")

    @field_validator("pu_vector")
    @classmethod
    def _check_pu_vector(cls, value: dict[str, float] | None) -> dict[str, float] | None:
        if value is None:
            return None
        validate_composition(value, "pu_vector")
        if not all(n.startswith("Pu-") for n in value):
            raise ValueError("pu_vector may only contain Pu isotopes")
        return value

    @model_validator(mode="after")
    def _check_kind_fields(self) -> Fuel:
        if self.kind is FuelKind.UOX:
            if self.enrichment_wt is None:
                raise ValueError(f"UOX fuel {self.name!r} needs enrichment_wt")
        elif self.kind is FuelKind.MOX:
            missing = [
                f for f in ("pu_content_wt", "pu_vector_source", "u_matrix") if getattr(self, f) is None
            ]
            if missing:
                raise ValueError(f"MOX fuel {self.name!r} needs {', '.join(missing)}")
            if self.pu_vector_source is PuVectorSource.FIXED and self.pu_vector is None:
                raise ValueError(f"MOX fuel {self.name!r} with a fixed Pu vector needs pu_vector")
        elif self.kind is FuelKind.CUSTOM and self.composition is None:
            raise ValueError(f"CUSTOM fuel {self.name!r} needs composition")
        return self
