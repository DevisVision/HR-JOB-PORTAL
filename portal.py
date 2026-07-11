import streamlit as st
import pandas as pd
import json
import urllib.parse
import os

st.set_page_config(page_title="HR Live Job Portal", page_icon="🔍", layout="wide")

st.title("🔍 DE & GenAI Job Portal")
st.markdown("---")

# Load data from the local JSON file
DATA_FILE = "data/jobs.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return pd.DataFrame(json.load(f))
    return pd.DataFrame()

df = load_data()

# Search Bar
search_query = st.text_input("🔍 Search for skills or roles...", placeholder="e.g., Spark, GenAI, Python")

if not df.empty:
    # Filter functionality
    if search_query:
        mask = df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)
        df = df[mask]

    st.write(f"Showing {len(df)} jobs")

    # Display Jobs
    for _, row in df.iterrows():
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(row.get('title', 'No Title'))
                st.write(f"**Company:** {row.get('company', 'N/A')} | **Skills:** {row.get('skills', 'N/A')}")
            with col2:
                # Construct WhatsApp message
                msg = f"Check out this role: {row.get('title')} at {row.get('company')}. Apply here: {row.get('link')}"
                wa_url = f"https://wa.me/?text={urllib.parse.quote(msg)}"
                st.link_button("Share on WhatsApp 📱", wa_url)
else:
    st.warning("No job data found. Please ensure 'data/jobs.json' is populated.")