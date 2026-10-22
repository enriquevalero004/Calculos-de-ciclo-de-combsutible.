"""Smoke test: every Streamlit page renders without exceptions."""

import sys
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from fcsim.io import data_dir, load_scenario

APP = Path(__file__).resolve().parents[1] / "app"
PAGES = [APP / "Home.py", *sorted((APP / "pages").glob("*.py"))]


@pytest.fixture(autouse=True)
def app_on_path(monkeypatch):
    monkeypatch.syspath_prepend(str(APP))


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.stem)
@pytest.mark.parametrize("with_scenario", [False, True])
def test_page_renders(page, with_scenario):
    at = AppTest.from_file(str(page), default_timeout=30)
    if with_scenario:
        at.session_state["scenario"] = load_scenario(data_dir() / "scenarios" / "demo_open_cycle.yaml")
    at.run()
    assert not at.exception
    assert any("NFCSS" in c.value for c in at.caption)
