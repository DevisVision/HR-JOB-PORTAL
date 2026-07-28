import streamlit as st

st.set_page_config(layout="wide")

st.markdown(
    """
    <h1 style="color:red;">HTML Works</h1>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="
    background:#2563EB;
    color:white;
    padding:20px;
    border-radius:15px;">
    VisionBoard
    </div>
    """,
    unsafe_allow_html=True,
)