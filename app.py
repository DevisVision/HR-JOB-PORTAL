"""
=========================================================
VisionBoard Career Portal
Main Application
=========================================================
Clean Client-Facing Version
=========================================================
"""

import streamlit as st

from utils.helpers import load_css

from components.header import show_header
from components.footer import show_footer
from components.filters import show_filters

from pages.home import show_home

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

load_css("assets/css/style.css")


# =========================================================
# STREAMLIT DEFAULT UI
# =========================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    /* Remove default page padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 1450px;
    }

    /* Remove unnecessary sidebar */
    [data-testid="stSidebar"] {
        display: none;
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


# =========================================================
# SEARCH + FILTERS
# =========================================================

filters = show_filters()


# =========================================================
# MAIN JOB RESULTS
# =========================================================

show_home(*filters)


# =========================================================
# FOOTER
# =========================================================

show_footer()