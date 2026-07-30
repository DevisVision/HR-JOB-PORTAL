"""
=========================================================
VisionBoard Career Portal
Professional Header
=========================================================
"""

from pathlib import Path
import streamlit as st


LOGO = Path("assets/VisionBoard.png")


def show_header():

    st.markdown(
        """
        <style>

        .vb-header-title {
            color: #0F4C81;
            font-size: 28px;
            font-weight: 800;
            line-height: 1.2;
        }

        .vb-header-subtitle {
            color: #64748B;
            font-size: 13px;
            margin-top: 5px;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):

        left, right = st.columns(
            [6, 4],
            vertical_alignment="center",
        )

        with left:

            logo_col, text_col = st.columns(
                [1, 7],
                vertical_alignment="center",
            )

            with logo_col:

                if LOGO.exists():

                    st.image(
                        str(LOGO),
                        width=150,
                    )

            with text_col:

                st.markdown(
                    "## VisionBoard Career Portal"
                )

                st.caption(
                    "Discover the latest opportunities from Fortune 500 "
                    "companies across India and worldwide."
                )

        with right:

           # c1, c2 = st.columns(2)

           # with c1:

               # st.info(" India Jobs ")

            #with c2:

             #   st.info(" Remote Jobs")

            st.success(
                "✔ Updated Every 6 Hours"
            )