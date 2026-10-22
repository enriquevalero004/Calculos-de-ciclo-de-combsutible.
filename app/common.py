"""Helpers shared by all Streamlit pages."""

from __future__ import annotations

import streamlit as st

from fcsim.models import Scenario
from i18n import t

SCENARIO_KEY = "scenario"


def page_header(title_key: str) -> None:
    st.set_page_config(page_title=f"fcsim · {t(title_key)}", layout="wide")
    st.title(t(title_key))
    st.caption(t("disclaimer"))


def current_scenario() -> Scenario | None:
    return st.session_state.get(SCENARIO_KEY)


def placeholder_banner(scenario: Scenario) -> None:
    paths = scenario.placeholders()
    if paths:
        st.warning(t("placeholders_warning", n=len(paths)))
        with st.expander(t("placeholders_list")):
            st.code("\n".join(paths), language=None)


def require_scenario() -> Scenario | None:
    scenario = current_scenario()
    if scenario is None:
        st.info(t("no_scenario"))
    else:
        placeholder_banner(scenario)
    return scenario
