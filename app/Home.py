"""fcsim Streamlit entry point: run with ``streamlit run app/Home.py``."""

from __future__ import annotations

import streamlit as st
from pydantic import ValidationError

from common import SCENARIO_KEY, current_scenario, page_header, placeholder_banner
from fcsim.io import data_dir, list_templates, load_scenario, scenario_from_yaml
from i18n import t

page_header("app_title")
st.write(t("home_intro"))

st.header(t("scenario_section"))
names = list_templates("scenarios")
col_pick, col_button = st.columns([3, 1], vertical_alignment="bottom")
choice = col_pick.selectbox(t("load_demo"), names)
if col_button.button(t("load"), disabled=not names):
    st.session_state[SCENARIO_KEY] = load_scenario(data_dir() / "scenarios" / f"{choice}.yaml")

uploaded = st.file_uploader(t("upload_yaml"), type=["yaml", "yml"])
if uploaded is not None:
    try:
        st.session_state[SCENARIO_KEY] = scenario_from_yaml(uploaded.getvalue().decode("utf-8"))
    except (ValidationError, ValueError) as error:
        st.error(t("invalid_yaml", error=error))

scenario = current_scenario()
if scenario is not None:
    st.success(t("loaded", name=scenario.name, start=scenario.start_year, end=scenario.end_year))
    placeholder_banner(scenario)
