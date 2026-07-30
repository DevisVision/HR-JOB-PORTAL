"""
=========================================================
VisionBoard Career Portal
Professional Footer
=========================================================
"""

from pathlib import Path
import streamlit as st


LOGO = "assets/VisionBoard.png"


def show_footer():

    st.divider()

    c1, c2, c3, c4 = st.columns(
        [3, 2, 2, 2]
    )

    # =====================================================
    # ABOUT
    # =====================================================

    with c1:

        if Path(LOGO).exists():

            st.image(
                LOGO,
                width=150,
            )

        st.markdown(
            "### VisionBoard Career Portal"
        )

        st.caption(
            "AI-powered job platform connecting professionals "
            "with opportunities in Data Engineering, Azure, "
            "Databricks, Python, Spark, AI, Machine Learning, "
            "Cloud and Analytics."
        )

    # =====================================================
    # PORTAL
    # =====================================================

    with c2:

        st.markdown("### Portal")

        st.write("🏠 Home")
        st.write("💼 Jobs")
        st.write("🏢 Companies")
        st.write("⭐ Saved Jobs")
        st.write("📊 Analytics")

    # =====================================================
    # RESOURCES
    # =====================================================

    with c3:

        st.markdown("### Resources")

        st.write("About Us")
        st.write("Careers")
        st.write("Privacy Policy")
        st.write("Terms & Conditions")
        st.write("Contact")

    # =====================================================
    # CONNECT
    # =====================================================

    with c4:

        st.markdown("### Connect")

        st.write("LinkedIn")
        st.write("GitHub")
        st.write("YouTube")

        st.write(
            "visionboardt1@gmail.com"
        )

    st.divider()

    left, right = st.columns(
        [4, 1]
    )

    with left:

        st.caption(
            "© 2026 VisionBoard Career Portal. "
            "All Rights Reserved."
        )

    with right:

        st.caption(
            "Career Portal v1.0"
        )