"""
Job Details Page (pages/job_details.py)
"""

import streamlit as st

from database.db_service import get_jobs

st.set_page_config(
    page_title="Job Details",
    page_icon="💼",
    layout="wide"
)

jobs = get_jobs(limit=200)

st.title("💼 Job Details")

if not jobs:
    st.warning("No jobs available.")
    st.stop()

# -----------------------------
# Select Job
# -----------------------------

titles = {
    f"{job['title']} | {job['company']}": job
    for job in jobs
}

selected = st.selectbox(
    "Select Job",
    list(titles.keys())
)

job = titles[selected]

# -----------------------------
# Header
# -----------------------------

st.markdown(f"""
<div class="job-header">

<h2>{job['title']}</h2>

<h4>{job['company']}</h4>

</div>
""", unsafe_allow_html=True)

# -----------------------------
# Information
# -----------------------------

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Location", job["location"])

with c2:
    st.metric("Country", job["country"])

with c3:
    st.metric("Employment", job["employment_type"])

st.divider()

# -----------------------------
# Skills
# -----------------------------

st.subheader("Skills")

st.info(job["skills"])

# -----------------------------
# Description
# -----------------------------

st.subheader("Job Description")

st.write(job["description"])

st.divider()

# -----------------------------
# Apply
# -----------------------------

st.link_button(
    "🚀 Apply Now",
    job["apply_url"],
    use_container_width=True
)