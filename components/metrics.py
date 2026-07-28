"""
components/metrics.py
"""

import streamlit as st


def show_metrics(metrics):

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            label="💼 Total Jobs",
            value=metrics["total_jobs"],
        )

    with c2:
        st.metric(
            label="🇮🇳 India Jobs",
            value=metrics["india_jobs"],
        )

    with c3:
        st.metric(
            label="🌍 Remote Jobs",
            value=metrics["remote_jobs"],
        )

    with c4:
        st.metric(
            label="🔄 Last Sync",
            value=metrics["last_sync"],
        )

    st.divider()