from __future__ import annotations

import streamlit as st

from common import page_header, require_scenario
from i18n import t

page_header("page_reactors")
scenario = require_scenario()
if scenario is not None:
    st.json(scenario.model_dump(mode="json", exclude_none=True)["reactor_types"], expanded=False)
st.info(t("coming_soon", milestone="M1"))
