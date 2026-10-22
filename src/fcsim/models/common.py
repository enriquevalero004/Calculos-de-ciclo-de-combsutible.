"""Shared types for the data model.

Missing nuclear or plant data is never filled in from memory: it is stored as
the literal string ``"PLACEHOLDER"`` so that it is visible in the YAML file,
reported by :func:`find_placeholders` and flagged in the UI.
"""

from __future__ import annotations

import re
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PLACEHOLDER = "PLACEHOLDER"
Placeholder = Literal["PLACEHOLDER"]

# Dimensionless fraction in [0, 1].
Fraction = Annotated[float, Field(ge=0.0, le=1.0)]
# Weight percent in [0, 100].
WeightPercent = Annotated[float, Field(ge=0.0, le=100.0)]
PositiveFloat = Annotated[float, Field(gt=0.0)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]

# Nuclide identifiers such as "U-235", "Pu-239" or "Am-242m".
NUCLIDE_PATTERN = re.compile(r"^[A-Z][a-z]?-\d{1,3}m?$")

COMPOSITION_TOLERANCE = 1e-6


class FcsimModel(BaseModel):
    """Base class: unknown keys are errors, assignments are validated."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


def validate_composition(composition: dict[str, float], label: str) -> dict[str, float]:
    """Check nuclide names and that mass fractions are non-negative and sum to 1."""
    for nuclide, fraction in composition.items():
        if not NUCLIDE_PATTERN.match(nuclide):
            raise ValueError(f"{label}: invalid nuclide name {nuclide!r} (expected e.g. 'U-235')")
        if fraction < 0.0:
            raise ValueError(f"{label}: negative mass fraction for {nuclide}")
    total = sum(composition.values())
    if abs(total - 1.0) > COMPOSITION_TOLERANCE:
        raise ValueError(f"{label}: mass fractions sum to {total!r}, expected 1")
    return composition


def is_placeholder(value: Any) -> bool:
    return isinstance(value, str) and value == PLACEHOLDER


def find_placeholders(obj: Any, prefix: str = "") -> list[str]:
    """Return the dotted paths of every PLACEHOLDER value inside ``obj``."""
    paths: list[str] = []
    if is_placeholder(obj):
        return [prefix]
    if isinstance(obj, BaseModel):
        items = ((name, getattr(obj, name)) for name in type(obj).model_fields)
    elif isinstance(obj, dict):
        items = ((str(k), v) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        items = ((f"[{i}]" if not _named(v) else v.name, v) for i, v in enumerate(obj))
    else:
        return paths
    for key, value in items:
        path = f"{prefix}.{key}" if prefix and not key.startswith("[") else f"{prefix}{key}"
        paths.extend(find_placeholders(value, path))
    return paths


def _named(value: Any) -> bool:
    return isinstance(value, BaseModel) and isinstance(getattr(value, "name", None), str)
