"""Fleets: a reactor type with its deployment path."""

from __future__ import annotations

from pydantic import Field

from .common import FcsimModel, PositiveFloat
from .deployment import DeploymentPath


class FleetLink(FcsimModel):
    """Coupling to another fleet (e.g. breeder core + blankets, v2).

    The linked fleet's power is ``ratio`` times the power of ``fleet``.
    """

    fleet: str
    ratio: PositiveFloat


class Fleet(FcsimModel):
    """A fleet of one reactor type; may be a single macro-reactor of any power.

    Attributes:
        replaces: name of a fleet whose power is reduced by the power added here
            (one-to-one substitution, as in TFG phases IV-VI).
    """

    name: str = Field(min_length=1)
    reactor_type: str = Field(min_length=1)
    deployment: DeploymentPath = Field(default_factory=DeploymentPath)
    linked_to: FleetLink | None = None
    replaces: str | None = None
