"""
VisionBoard Sidebar
"""

import streamlit as st


def show_sidebar(metrics):

    st.markdown("## 🧭 Navigation")

    st.button("🏠 Home", use_container_width=True)
    st.button("💼 Jobs", use_container_width=True)
    st.button("🏢 Companies", use_container_width=True)
    st.button("⭐ Saved Jobs", use_container_width=True)
    st.button("📊 Analytics", use_container_width=True)

    st.divider()

    st.markdown("## 🌍 Job Location")

    st.radio(
        "",
        [
            "All Jobs",
            "India",
            "Rest of World",
            "Remote Only"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("## ⚡ Quick Filters")

    st.checkbox("Full Time", value=True)
    st.checkbox("Contract")
    st.checkbox("Internship")
    st.checkbox("Hybrid")
    st.checkbox("Remote")
    st.checkbox("Last 24 Hours")
    st.checkbox("Last 7 Days")