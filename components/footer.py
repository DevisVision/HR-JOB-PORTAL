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

    st.markdown("---")

    c1, c2, c3, c4 = st.columns([3, 2, 2, 2])

    # =====================================================
    # Logo + About
    # =====================================================

    with c1:

        if Path(LOGO).exists():
            st.image(LOGO, width=170)

        st.markdown("### VisionBoard Career Portal")

        st.write(
            """
AI-powered job platform connecting professionals with opportunities in
Data Engineering, Azure, Databricks, Python, Spark, AI, Machine Learning,
Cloud and Analytics.
"""
        )

    # =====================================================
    # Portal Links
    # =====================================================

    with c2:

        st.markdown("### Portal")

        st.page_link("app.py", label="🏠 Home")

        st.write("💼 Jobs")

        st.write("🏢 Companies")

        st.write("⭐ Saved Jobs")

        st.write("📊 Analytics")

    # =====================================================
    # Resources
    # =====================================================

    with c3:

        st.markdown("### Resources")

        st.write("About Us")

        st.write("Careers")

        st.write("Privacy Policy")

        st.write("Terms & Conditions")

        st.write("Contact")

    # =====================================================
    # Connect
    # =====================================================

    with c4:

        st.markdown("### Connect")

        st.write("LinkedIn")

        st.write("GitHub")

        st.write("YouTube")

        st.write("support@visionboard.ai")

    st.markdown("---")

    c1, c2 = st.columns([4, 1])

    with c1:

        st.caption(
            "© 2026 VisionBoard Career Portal. All Rights Reserved."
        )

    with c2:

        st.caption("Version 2.0")