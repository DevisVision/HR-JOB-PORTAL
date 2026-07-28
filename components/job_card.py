"""
=========================================================
VisionBoard Career Portal
Professional Job Card
=========================================================
"""

import streamlit as st


def show_job_card(job):
    """
    Render a professional job card.
    """

    title = job.get("title", "Job Title")
    company = job.get("company", "Unknown Company")
    location = job.get("location", "Location Not Available")
    employment = job.get("employment_type", "Not Specified")
    salary = job.get("salary", "Not Disclosed")
    posted = str(job.get("posted_date", ""))[:10]
    description = job.get("description", "No description available.")
    apply_url = job.get("apply_url", "#")

    logo = company[:1].upper()

    unique_id = (
        job.get("job_id")
        or job.get("id")
        or f"{title}_{company}_{location}_{posted}"
    )

    st.markdown(
        f"""
<style>

.job-card{{
    background:#FFFFFF;
    border:1px solid #E5E7EB;
    border-radius:18px;
    padding:20px;
    margin-bottom:18px;
    box-shadow:0 3px 12px rgba(0,0,0,.05);
}}

.job-header{{
    display:flex;
    gap:18px;
}}

.job-logo{{
    width:60px;
    height:60px;
    border-radius:14px;
    background:#0F4C81;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
    font-weight:bold;
}}

.job-title{{
    font-size:24px;
    font-weight:700;
    color:#1E293B;
}}

.job-company{{
    font-size:16px;
    color:#334155;
    margin-top:4px;
}}

.job-location{{
    color:#64748B;
    margin-top:6px;
}}

.job-tags{{
    margin-top:16px;
}}

.tag{{
    display:inline-block;
    background:#EFF6FF;
    border:1px solid #BFDBFE;
    color:#0F4C81;
    padding:6px 12px;
    border-radius:20px;
    margin-right:8px;
    font-size:13px;
    font-weight:600;
}}

</style>

<div class="job-card">

<div class="job-header">

<div class="job-logo">
{logo}
</div>

<div style="flex:1">

<div class="job-title">
{title}
</div>

<div class="job-company">
🏢 {company}
</div>

<div class="job-location">
📍 {location}
</div>

<div class="job-tags">

<span class="tag">
💼 {employment}
</span>

<span class="tag">
💰 {salary}
</span>

<span class="tag">
📅 {posted}
</span>

</div>

</div>

</div>

</div>
""",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2.2, 1.3, 1])

    with col1:

        if apply_url and apply_url != "#":
            st.link_button(
                "🚀 Apply Now",
                apply_url,
                use_container_width=True,
            )
        else:
            st.button(
                "🚀 Apply Now",
                disabled=True,
                use_container_width=True,
                key=f"apply_{unique_id}",
            )

    with col2:

        with st.expander("View Details"):
            st.write(description)

    with col3:

        st.button(
            "⭐ Save",
            key=f"save_{unique_id}",
            use_container_width=True,
        )