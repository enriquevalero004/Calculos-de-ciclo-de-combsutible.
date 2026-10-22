from __future__ import annotations

import streamlit as st

from common import page_header, require_scenario
from fcsim.io import scenario_to_yaml
from i18n import t

page_header("page_export")
scenario = require_scenario()
if scenario is not None:
    st.download_button(
        t("download_yaml"),
        data=scenario_to_yaml(scenario),
        file_name=f"{scenario.name.replace(' ', '_')}.yaml",
        mime="application/x-yaml",
    )
st.info(t("coming_soon", milestone="M5"))
