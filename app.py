"""
=========================================================
VisionBoard Career Portal
Main Application
=========================================================
Clean Client-Facing Version
=========================================================
"""

import streamlit as st
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from utils.helpers import load_css

from components.header import show_header
from components.footer import show_footer
from components.filters import show_filters

from pages.home import show_home

from database.db_service import (
    get_job_count,
    get_india_job_count,
    get_remote_job_count,
    get_last_successful_sync,
)

from services.sync_service import maybe_run_scheduled_sync


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
# AUTOMATIC 6-HOUR SYNCHRONIZATION
# =========================================================

# Streamlit Cloud does not keep a Python scheduler process alive reliably.
# Therefore the existing sync pipeline is invoked on app access only when
# the last successful sync is older than 6 hours. No job filtering, ranking,
# ordering, or freshness logic is changed here.
if "sync_checked" not in st.session_state:
    st.session_state.sync_checked = True
    try:
        with st.spinner("Checking job synchronization..."):
            maybe_run_scheduled_sync(6)
    except Exception as exc:
        st.warning(f"Job sync could not be completed: {exc}")


# =========================================================
# METRICS
# =========================================================

last_sync = get_last_successful_sync()


def format_sync_time(value):
    if not value:
        return "Not available"
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        ist = dt.astimezone(ZoneInfo("Asia/Kolkata"))
        return ist.strftime("%d %b %Y, %I:%M %p IST")
    except (TypeError, ValueError):
        return str(value)


formatted_last_sync = format_sync_time(last_sync)

# SQLite sync_log timestamps are stored in UTC. Display the expected
# next six-hour check in IST without changing the stored value.
next_sync_display = "Not available"
if last_sync:
    try:
        last_dt = datetime.fromisoformat(str(last_sync).replace("Z", "+00:00"))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        next_dt = last_dt.astimezone(ZoneInfo("Asia/Kolkata")) + timedelta(hours=6)
        next_sync_display = next_dt.strftime("%d %b %Y, %I:%M %p IST")
    except (TypeError, ValueError):
        next_sync_display = "Not available"

metrics = {
    "total_jobs": get_job_count(),
    "india_jobs": get_india_job_count(),
    "remote_jobs": get_remote_job_count(),
    "last_sync": last_sync or "Not available",
}


# =========================================================
# HEADER
# =========================================================

show_header()

if last_sync:
    st.caption(
        f"🔄 Last sync completed: {formatted_last_sync} • Next sync check: {next_sync_display}"
    )
else:
    st.caption("🔄 Last sync completed: Not available • Initial synchronization will run automatically")


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