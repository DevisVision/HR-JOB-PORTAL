import streamlit as st

from utils.helpers import load_css

from components.header import show_header
from components.sidebar import show_sidebar
from components.footer import show_footer
from components.filters import show_filters

from pages.home import show_home

from database.db_service import (
    get_job_count,
    get_india_job_count,
    get_remote_job_count,
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="VisionBoard Career Portal",
    page_icon="assets/VisionBoard.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_css()

# =====================================================
# METRICS
# =====================================================

metrics = {
    "total_jobs": get_job_count(),
    "india_jobs": get_india_job_count(),
    "remote_jobs": get_remote_job_count(),
    "last_sync": "Every 6 Hours",
}

# =====================================================
# HEADER
# =====================================================

show_header()

# =====================================================
# MAIN LAYOUT
# =====================================================

left, right = st.columns([1, 4], gap="large")

# =====================================================
# SIDEBAR
# =====================================================

with left:
    show_sidebar(metrics)

# =====================================================
# MAIN CONTENT
# =====================================================

with right:

    keyword, category, employment, search_clicked = show_filters()

    show_home(
        keyword=keyword,
        category=category,
        employment=employment,
        source="All",
        posted="Any Time",
    )

# =====================================================
# FOOTER
# =====================================================

show_footer()