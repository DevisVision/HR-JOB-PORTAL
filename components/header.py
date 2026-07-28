"""
=========================================================
VisionBoard Professional Header
=========================================================
"""

from pathlib import Path
import streamlit as st


def show_header():
    """
    Professional Header
    """

    logo = Path("assets/VisionBoard.png")

    left, right = st.columns([1, 5])

    # ----------------------------------------------------
    # Logo
    # ----------------------------------------------------

    with left:

        if logo.exists():

            st.image(str(logo), width=130)

    # ----------------------------------------------------
    # Title
    # ----------------------------------------------------

    with right:

        st.markdown(
            """
            <h1 style="
                margin-bottom:0;
                color:#0F4C81;
                font-weight:700;
            ">
                VisionBoard Career Portal
            </h1>

            <div style="
                color:#64748B;
                font-size:16px;
                margin-top:-5px;
            ">
                Discover the latest jobs from multiple job providers across India and worldwide.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()