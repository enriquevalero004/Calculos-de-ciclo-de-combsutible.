"""Deployment paths: net electrical power of a fleet over time.

Only the data structure lives here; evaluation is in ``fcsim.deployment`` (M1).
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field, model_validator

from .common import FcsimModel, NonNegativeFloat


class SegmentFunction(str, Enum):
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    LOGISTIC = "logistic"


class Segment(FcsimModel):
    """One functional segment on the closed year interval [t0_year, t1_year].

    ``p0_mwe`` defaults to the end power of the previous segment (continuity).
    Growing and declining paths are the same family with the sign of p1 - p0.
    ``k`` is the shape parameter of exponential, logarithmic and logistic segments.
    """

    function: SegmentFunction
    t0_year: int
    t1_year: int
    p0_mwe: NonNegativeFloat | None = None
    p1_mwe: NonNegativeFloat | None = None
    k: float | None = None
    continuous: bool = True

    @model_validator(mode="after")
    def _check(self) -> Segment:
        if self.t1_year <= self.t0_year:
            raise ValueError(f"segment {self.t0_year}-{self.t1_year}: t1_year must be after t0_year")
        if self.function is not SegmentFunction.CONSTANT and self.p1_mwe is None:
            raise ValueError(f"{self.function.value} segment needs p1_mwe")
        needs_k = (SegmentFunction.EXPONENTIAL, SegmentFunction.LOGARITHMIC, SegmentFunction.LOGISTIC)
        if self.function in needs_k and self.k is None:
            raise ValueError(f"{self.function.value} segment needs k")
        return self


class DeploymentPath(FcsimModel):
    """Functional segments followed by manual yearly edits.

    Attributes:
        manual_delta_mwe: {year: MWe added (positive) or removed (negative)}.
        manual_set_mwe: {year: MWe the power is fixed to}; applied after deltas.
    """

    segments: list[Segment] = Field(default_factory=list)
    manual_delta_mwe: dict[int, float] = Field(default_factory=dict)
    manual_set_mwe: dict[int, NonNegativeFloat] = Field(default_factory=dict)
    round_to_units: bool = False

    @model_validator(mode="after")
    def _check_segments(self) -> DeploymentPath:
        if self.segments and self.segments[0].p0_mwe is None:
            raise ValueError("the first deployment segment needs p0_mwe")
        for prev, seg in zip(self.segments, self.segments[1:]):
            if seg.t0_year < prev.t1_year:
                raise ValueError(
                    f"segments overlap: {prev.t0_year}-{prev.t1_year} and {seg.t0_year}-{seg.t1_year}"
                )
            prev_end = prev.p0_mwe if prev.p1_mwe is None else prev.p1_mwe
            if seg.continuous and seg.p0_mwe is not None and prev_end is not None:
                if abs(seg.p0_mwe - prev_end) > 1e-9 * max(1.0, abs(prev_end)):
                    raise ValueError(
                        f"segment starting {seg.t0_year} is marked continuous but p0_mwe="
                        f"{seg.p0_mwe} differs from the previous end power {prev_end}"
                    )
        return self
