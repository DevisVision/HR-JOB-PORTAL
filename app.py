"""
=========================================================
VisionBoard Career Portal
Main Application
=========================================================
"""

import streamlit as st

# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------

from utils.helpers import load_css

# ---------------------------------------------------------
# Components
# ---------------------------------------------------------

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer
from components.filters import show_filters

# ---------------------------------------------------------
# Pages
# ---------------------------------------------------------

from pages.home import show_home

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

from database.db_service import (
    get_job_count,
    get_india_job_count,
    get_remote_job_count,
)

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="VisionBoard Career Portal",
    page_icon="assets/VisionBoard.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# LOAD CSS
# =========================================================

#load_css("styles/style.css")
load_css("assets/css/style.css")

# =========================================================
# HIDE STREAMLIT MENU
# =========================================================

st.markdown(
    """
<style>

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# METRICS
# =========================================================

metrics = {

    "total_jobs": get_job_count(),

    "india_jobs": get_india_job_count(),

    "remote_jobs": get_remote_job_count(),

    "last_sync": "6 Hours Ago",

}

# =========================================================
# HEADER
# =========================================================

show_header()

st.write("")

# =========================================================
# MAIN LAYOUT
# =========================================================

left, right = st.columns(
    [1, 4],
    gap="large",
)

# =========================================================
# LEFT PANEL
# =========================================================

with left:

    show_sidebar(metrics)

# =========================================================
# RIGHT PANEL
# =========================================================

with right:

    filters = show_filters()

    st.write("")

    show_home(*filters)

# =========================================================
# FOOTER
# =========================================================

st.divider()
#show_home(*filters)
show_footer()