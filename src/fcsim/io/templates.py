"""Access to the editable templates and scenarios in the repository's ``data/``."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

from fcsim.models import Fuel, ReactorType


def data_dir() -> Path:
    """The ``data/`` directory: $FCSIM_DATA_DIR, or the one at the repository root."""
    env = os.environ.get("FCSIM_DATA_DIR")
    return Path(env) if env else Path(__file__).resolve().parents[3] / "data"


def list_templates(kind: str) -> list[str]:
    """Template names (file stems) for ``kind`` in {"reactors", "fuels"}, or scenario names."""
    folder = data_dir() / ("scenarios" if kind == "scenarios" else f"templates/{kind}")
    return sorted(p.stem for p in folder.glob("*.yaml"))


def _read(kind: str, name: str) -> dict:
    path = data_dir() / "templates" / kind / f"{name}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_reactor_template(name: str) -> ReactorType:
    return ReactorType.model_validate(_read("reactors", name))


def load_fuel_template(name: str) -> Fuel:
    return Fuel.model_validate(_read("fuels", name))
