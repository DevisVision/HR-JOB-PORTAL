"""
=========================================================
VisionBoard Professional Sidebar
=========================================================
"""

import streamlit as st


def show_sidebar(metrics):

    # ----------------------------------------------------
    # Navigation
    # ----------------------------------------------------

    st.markdown("## 📋 Navigation")

    st.button("🏠 Dashboard", use_container_width=True)

    st.button("💼 Jobs", use_container_width=True)

    st.button("🏢 Companies", use_container_width=True)

    st.button("⭐ Saved Jobs", use_container_width=True)

    st.button("📊 Analytics", use_container_width=True)

    st.button("⚙ Settings", use_container_width=True)

    st.divider()

    # ----------------------------------------------------
    # Statistics
    # ----------------------------------------------------

    st.markdown("## 📊 Portal Statistics")

    c1, c2 = st.columns(2)

    with c1:
        st.metric("Jobs", metrics["total_jobs"])

    with c2:
        st.metric("India", metrics["india_jobs"])

    c3, c4 = st.columns(2)

    with c3:
        st.metric("Remote", metrics["remote_jobs"])

    with c4:
        st.metric("Sync", metrics["last_sync"])

    st.divider()

    # ----------------------------------------------------
    # Quick Filters
    # ----------------------------------------------------

    st.markdown("## 🌍 Quick Filters")

    location = st.selectbox(
        "Location",
        [
            "All Jobs",
            "India",
            "Rest of World",
            "Remote Only",
        ],
        label_visibility="collapsed",
    )

    employment = st.multiselect(
        "Employment",
        [
            "Full Time",
            "Contract",
            "Internship",
            "Part Time",
            "Hybrid",
            "Remote",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    # ----------------------------------------------------
    # Top Companies
    # ----------------------------------------------------

    st.markdown("## 🏢 Top Companies")

    companies = [
        "Google",
        "Microsoft",
        "Amazon",
        "Infosys",
        "TCS",
        "Accenture",
    ]

    for company in companies:
        st.markdown(f"• {company}")

    st.divider()

    st.caption("VisionBoard Career Portal v1.0")

    return location, employment