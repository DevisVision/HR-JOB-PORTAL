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
# Logo
# -------------------------------------------------------

def get_logo_base64():

    logo_path = Path("assets") / "VisionBoard.png"

    if logo_path.exists():

        with open(logo_path, "rb") as image:

            return base64.b64encode(image.read()).decode()

    return ""


# -------------------------------------------------------
# Header
# -------------------------------------------------------

def show_header():

    logo = get_logo_base64()

    st.markdown(
        f"""
        <style>

        .vb-navbar{{
            background:#ffffff;
            border:1px solid #E6ECF2;
            border-radius:16px;
            padding:18px 28px;
            margin-bottom:20px;
            box-shadow:0 8px 25px rgba(0,0,0,.08);
        }}

        .vb-row{{
            display:flex;
            justify-content:space-between;
            align-items:center;
        }}

        .vb-left{{
            display:flex;
            align-items:center;
            gap:18px;
        }}

        .vb-logo{{
            width:58px;
            height:58px;
            border-radius:12px;
        }}

        .vb-title{{
            font-size:30px;
            font-weight:800;
            color:#0F4C81;
            margin:0;
        }}

        .vb-subtitle{{
            color:#5E6C84;
            font-size:14px;
            margin-top:4px;
        }}

        .vb-right{{
            display:flex;
            gap:12px;
            align-items:center;
        }}

        .vb-chip{{
            background:#F3F8FF;
            color:#0F4C81;
            padding:8px 18px;
            border-radius:30px;
            font-size:13px;
            font-weight:600;
            border:1px solid #D6E6F7;
        }}

        .vb-sync{{
            background:#EAF7EF;
            color:#2E7D32;
        }}

        </style>

        <div class="vb-navbar">

            <div class="vb-row">

                <div class="vb-left">

                    <img class="vb-logo"
                    src="data:image/png;base64,{logo}">

                    <div>

                        <div class="vb-title">
                        VisionBoard Career Portal
                        </div>

                        <div class="vb-subtitle">
                        Discover the latest opportunities from Fortune 500 companies across India and worldwide.
                        </div>

                    </div>

                </div>

                <div class="vb-right">

                    <div class="vb-chip">
                    🇮🇳 India Jobs First
                    </div>

                    <div class="vb-chip">
                    🌍 Remote Jobs
                    </div>

                    <div class="vb-chip vb-sync">
                    ✔ Updated Every 6 Hours
                    </div>

                </div>

            </div>

        </div>

        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="height:10px"></div>
        """,
        unsafe_allow_html=True,
    )