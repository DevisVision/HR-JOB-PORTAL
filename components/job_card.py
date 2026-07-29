"""
=========================================================
VisionBoard Career Portal
Professional Job Card
=========================================================
"""

from pathlib import Path
from datetime import datetime
import base64
import streamlit as st


# =========================================================
# COMPANY PRIORITY
# =========================================================

FORTUNE_COMPANIES = {
    "IBM",
    "UST",
    "EY",
    "ERNST & YOUNG",
    "KPMG",
    "DELOITTE",
    "ACCENTURE",
    "COGNIZANT",
    "WIPRO",
    "CAPGEMINI",
    "TECH MAHINDRA",
    "CISCO",
    "ALLIANZ",
    "MICROSOFT",
    "GOOGLE",
    "AMAZON",
    "ORACLE",
    "TCS",
    "HCL",
    "INFOSYS",
    "IBS"
}


# =========================================================
# COMPANY LOGO
# =========================================================

def get_company_logo(company):

    company = company.lower().replace(" ", "_")

    logo = Path("assets/logos") / f"{company}.png"

    if logo.exists():

        with open(logo, "rb") as img:

            return base64.b64encode(img.read()).decode()

    return None


# =========================================================
# RELATIVE DATE
# =========================================================

def format_posted_date(posted):

    if not posted:
        return "Recently"

    try:

        posted = str(posted)[:10]

        post_date = datetime.strptime(posted, "%Y-%m-%d")

        days = (datetime.now() - post_date).days

        if days <= 0:
            return "Today"

        if days == 1:
            return "Yesterday"

        return f"{days} days ago"

    except Exception:

        return "Recently"


# =========================================================
# JOB CARD
# =========================================================

def show_job_card(job):

    title = job.get("title", "Job Title")

    company = job.get("company", "Unknown Company")

    location = job.get("location", "Location")

    country = job.get("country", "")

    employment = job.get("employment_type", "Full Time")

    salary = job.get("salary") or "Salary Not Mentioned"

    description = job.get("description", "")

    posted = format_posted_date(job.get("posted_date"))

    apply_url = job.get("apply_url", "")

    skills = job.get("skills", "")

    logo = get_company_logo(company)

    fortune = company.upper() in FORTUNE_COMPANIES

    unique_key = (
        job.get("job_id")
        or f"{title}_{company}_{location}"
    )

    badge = ""

    if fortune:
        badge = """
        <span style="
            background:#FFF8E1;
            color:#F57C00;
            padding:4px 10px;
            border-radius:15px;
            font-size:11px;
            font-weight:700;">
            ⭐ Fortune Company
        </span>
        """

    logo_html = ""

    if logo:

        logo_html = f"""
        <img
            src="data:image/png;base64,{logo}"
            style="
                width:65px;
                height:65px;
                border-radius:12px;
                object-fit:contain;
                border:1px solid #E5E7EB;
                padding:6px;
                background:white;">
        """

    else:

        logo_html = f"""
        <div style="
            width:65px;
            height:65px;
            border-radius:12px;
            background:#0F4C81;
            color:white;
            display:flex;
            justify-content:center;
            align-items:center;
            font-size:26px;
            font-weight:bold;">
            {company[:1].upper()}
        </div>
        """

    skill_html = ""

    if skills:

        for skill in str(skills).split(",")[:6]:

            skill_html += f"""
            <span style="
                background:#EAF3FF;
                color:#1565C0;
                padding:5px 12px;
                margin:3px;
                border-radius:20px;
                font-size:12px;
                display:inline-block;">
                {skill.strip()}
            </span>
            """

    st.markdown(
        f"""
<div style="
background:white;
border:1px solid #E5E7EB;
border-radius:18px;
padding:22px;
margin-bottom:18px;
box-shadow:0 6px 18px rgba(0,0,0,.06);">

<div style="display:flex;gap:18px;">

{logo_html}

<div style="flex:1;">

<div style="
font-size:24px;
font-weight:700;
color:#0F4C81;">

{title}

</div>

<div style="
font-size:17px;
font-weight:600;
margin-top:4px;">

🏢 {company}

{badge}

</div>

<div style="margin-top:8px;color:#555;">

📍 {location}

{' | ' + country if country else ''}

</div>

<div style="margin-top:12px;">

<span style="
background:#EEF7EE;
padding:5px 10px;
border-radius:15px;
font-size:12px;
margin-right:6px;">

💼 {employment}

</span>

<span style="
background:#FFF4E5;
padding:5px 10px;
border-radius:15px;
font-size:12px;
margin-right:6px;">

💰 {salary}

</span>

<span style="
background:#F3F4F6;
padding:5px 10px;
border-radius:15px;
font-size:12px;">

🕒 {posted}

</span>

</div>

<div style="margin-top:15px;">

{skill_html}

</div>

</div>

</div>

</div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([2.2, 1.4, 1])

    with col1:

        if apply_url:

            st.link_button(
                "🚀 Apply Now",
                apply_url,
                use_container_width=True,
            )

        else:

            st.button(
                "🚀 Apply",
                disabled=True,
                key=f"apply_{unique_key}",
                use_container_width=True,
            )

    with col2:

        with st.expander("📄 Job Description"):

            st.write(description if description else "Description not available.")

    with col3:

        st.button(
            "⭐ Save",
            key=f"save_{unique_key}",
            use_container_width=True,
        )

    st.write("")