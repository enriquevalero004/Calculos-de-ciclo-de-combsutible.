"""Scenario <-> YAML. The same scenario always serialises to the same text."""

from __future__ import annotations

from pathlib import Path

import yaml

from fcsim.models import Scenario


def scenario_to_yaml(scenario: Scenario) -> str:
    data = scenario.model_dump(mode="json", exclude_none=True)
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)


def scenario_from_yaml(text: str) -> Scenario:
    return Scenario.model_validate(yaml.safe_load(text))


def dump_scenario(scenario: Scenario, path: str | Path) -> None:
    Path(path).write_text(scenario_to_yaml(scenario), encoding="utf-8")


def load_scenario(path: str | Path) -> Scenario:
    return scenario_from_yaml(Path(path).read_text(encoding="utf-8"))
