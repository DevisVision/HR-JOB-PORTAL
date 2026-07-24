"""
=========================================================
VisionBoard Career Portal
Professional Header
=========================================================
"""

from pathlib import Path
import base64
import streamlit as st


# -------------------------------------------------------
# Load Logo
# -------------------------------------------------------

def _load_logo():

    logo_path = Path("assets/VisionBoard.png")

    if logo_path.exists():
        with open(logo_path, "rb") as img:
            return base64.b64encode(img.read()).decode()

    return ""


# -------------------------------------------------------
# Header
# -------------------------------------------------------

def show_header():

    logo = _load_logo()

    c1, c2 = st.columns([1, 5])

    with c1:

        if logo:
            st.image("assets/VisionBoard.png", width=80)

    with c2:

        st.markdown(
            """
            <h1 style="
                margin-bottom:0;
                color:#0F172A;
                font-size:42px;
                font-weight:800;
            ">
            🚀 VisionBoard Career Portal
            </h1>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            "AI-powered Job Search Platform for Data Engineering • AI • Cloud • Analytics"
        )

    st.write("")

    c1, c2, c3 = st.columns([5, 2, 1])

    with c1:

        st.text_input(
            "Search Jobs",
            placeholder="Search Jobs, Skills or Companies...",
            label_visibility="collapsed",
            key="header_search",
        )

    with c2:

        st.selectbox(
            "Category",
            [
                "All Jobs",
                "India",
                "Rest of World",
                "Remote"
            ],
            label_visibility="collapsed",
            key="header_category",
        )

    with c3:
        st.empty()
        #st.button(
       #     "Login",
       #     use_container_width=True,
       #     key="login_button",
        #)

    st.divider()