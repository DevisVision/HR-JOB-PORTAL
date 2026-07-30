"""
=========================================================
VisionBoard Career Portal
Sidebar Filters
=========================================================
"""

import streamlit as st


def show_sidebar(metrics):

    st.markdown("## 🧭 Navigation")

    st.button(
        "🏠 Home",
        use_container_width=True,
    )

    st.button(
        "💼 Jobs",
        use_container_width=True,
    )

    st.button(
        "🏢 Companies",
        use_container_width=True,
    )

    st.button(
        "⭐ Saved Jobs",
        use_container_width=True,
    )

    st.button(
        "📊 Analytics",
        use_container_width=True,
    )

    st.divider()

    # =====================================================
    # LOCATION
    # =====================================================

    st.markdown("## 🌍 Job Location")

    location = st.radio(
        "Job Location",
        [
            "All Jobs",
            "India",
            "Rest of World",
            "Remote Only",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # =====================================================
    # QUICK FILTERS
    # =====================================================

    st.markdown("## ⚡ Quick Filters")

    full_time = st.checkbox(
        "Full Time"
    )

    contract = st.checkbox(
        "Contract"
    )

    internship = st.checkbox(
        "Internship"
    )

    hybrid = st.checkbox(
        "Hybrid"
    )

    remote = st.checkbox(
        "Remote"
    )

    last_24 = st.checkbox(
        "Last 24 Hours"
    )

    last_7 = st.checkbox(
        "Last 7 Days"
    )

    return {
        "location": location,
        "full_time": full_time,
        "contract": contract,
        "internship": internship,
        "hybrid": hybrid,
        "remote": remote,
        "last_24": last_24,
        "last_7": last_7,
    }