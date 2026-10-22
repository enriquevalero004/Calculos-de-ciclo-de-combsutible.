from __future__ import annotations

import streamlit as st

from common import page_header, require_scenario
from i18n import t

page_header("page_diagnostics")
require_scenario()
st.info(t("coming_soon", milestone="M4"))
