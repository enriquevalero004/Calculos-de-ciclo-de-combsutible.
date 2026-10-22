from pathlib import Path

import pytest

from fcsim.io import data_dir, load_scenario

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def demo_scenario():
    return load_scenario(data_dir() / "scenarios" / "demo_open_cycle.yaml")
