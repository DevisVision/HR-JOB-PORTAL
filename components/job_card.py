"""
=========================================================
VisionBoard Career Portal
Professional Job Card
=========================================================
"""

from pathlib import Path
import html
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote

import streamlit as st


# =========================================================
# COMPANY LOGOS
# =========================================================

COMPANY_LOGOS = {
    "IBM": "assets/company_logos/ibm.png",
    "COGNIZANT": "assets/company_logos/cognizant.png",
    "ACCENTURE": "assets/company_logos/accenture.png",
    "UST": "assets/company_logos/ust.png",
    "EY": "assets/company_logos/ey.png",
    "KPMG": "assets/company_logos/kpmg.png",
    "CAPGEMINI": "assets/company_logos/capgemini.png",
    "CISCO": "assets/company_logos/cisco.png",
    "WIPRO": "assets/company_logos/wipro.png",
    "INFOSYS": "assets/company_logos/infosys.png",
    "TCS": "assets/company_logos/tcs.png",
    "HCL": "assets/company_logos/hcl.png",
    "TECH MAHINDRA": "assets/company_logos/tech_mahindra.png",
    "ALLIANZ": "assets/company_logos/allianz.png",
    "MICROSOFT": "assets/company_logos/microsoft.png",
    "GOOGLE": "assets/company_logos/google.png",
    "AMAZON": "assets/company_logos/amazon.png",
    "ORACLE": "assets/company_logos/oracle.png",
    "DELOITTE": "assets/company_logos/deloitte.png",
    "PWC": "assets/company_logos/pwc.png",
}


FORTUNE_COMPANIES = set(COMPANY_LOGOS.keys())


# =========================================================
# HELPERS
# =========================================================

def get_company_logo(company):

    company_upper = str(company).strip().upper()

    for company_name, logo_path in COMPANY_LOGOS.items():

        if company_name in company_upper:

            path = Path(logo_path)

            if path.exists():
                return str(path)

    return None


def get_company_initial(company):

    company = str(company).strip()

    if not company:
        return "?"

    return company[0].upper()


# =========================================================
# POSTED DATE DISPLAY
# =========================================================

def format_posted_date(value):
    """
    Convert source timestamps such as
    2026-07-22T13:07:34Z into a user-friendly display.

    The database value is not modified.
    """

    raw = str(value or "").strip()

    if not raw:
        return ""

    try:
        parsed = datetime.fromisoformat(
            raw.replace("Z", "+00:00")
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=ZoneInfo("Asia/Kolkata")
            )
        else:
            parsed = parsed.astimezone(
                ZoneInfo("Asia/Kolkata")
            )

        now = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        age_seconds = (
            now - parsed
        ).total_seconds()

        if 0 <= age_seconds < 86400:
            hours = int(age_seconds // 3600)

            if hours < 1:
                minutes = max(
                    1,
                    int(age_seconds // 60),
                )
                return (
                    f"Posted {minutes} "
                    f"minute{'s' if minutes != 1 else ''} ago"
                )

            return (
                f"Posted {hours} "
                f"hour{'s' if hours != 1 else ''} ago"
            )

        if 0 <= age_seconds < 7 * 86400:
            days = int(age_seconds // 86400)
            return (
                f"Posted {days} "
                f"day{'s' if days != 1 else ''} ago"
            )

        return f"Posted {parsed.strftime('%d %b %Y')}"

    except (ValueError, TypeError, OverflowError):
        return raw


# =========================================================
# JOB CARD
# =========================================================

def show_job_card(job):

    title = str(
        job.get("title", "Untitled Position")
    ).strip()

    company = str(
        job.get("company", "Company Not Mentioned")
    ).strip()

    location = str(
        job.get("location", "Location Not Mentioned")
    ).strip()

    country = str(
        job.get("country", "")
    ).strip()

    employment = str(
        job.get("employment_type", "")
    ).strip()

    salary = str(
        job.get("salary", "")
    ).strip()

    posted = format_posted_date(
        job.get("posted_date", "")
    )

    description = str(
        job.get("description", "")
    ).strip()

    apply_url = str(
        job.get("apply_url", "")
    ).strip()

    logo_path = get_company_logo(company)

    initial = get_company_initial(company)

    # =====================================================
    # CARD
    # =====================================================

    with st.container(border=True):

        logo_col, content_col, action_col = st.columns(
            [1, 6, 1.5],
            vertical_alignment="top",
        )

        # =================================================
        # COMPANY LOGO
        # =================================================

        with logo_col:

            if logo_path:

                st.image(
                    logo_path,
                    width=64,
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                        width:58px;
                        height:58px;
                        border-radius:12px;
                        background:#0F4C81;
                        color:white;
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        font-size:24px;
                        font-weight:700;
                    ">
                        {initial}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # =================================================
        # JOB INFORMATION
        # =================================================

        with content_col:

            st.markdown(
                f"### {html.escape(title)}"
            )

            st.write(
                f"🏢 **{company}**"
            )

            if any(
                name in company.upper()
                for name in FORTUNE_COMPANIES
            ):

                st.caption(
                    "⭐ Preferred / Fortune Company"
                )

            location_text = location

            if country:

                if country.lower() not in location.lower():

                    location_text += f" | {country}"

            st.write(
                f"📍 {location_text}"
            )

            if employment:

                st.write(
                    f"💼 {employment}"
                )

            if salary and salary.lower() not in {
                "none",
                "null",
                "not mentioned",
                "salary not mentioned",
            }:

                st.write(
                    f"💰 {salary}"
                )

            if posted:

                st.write(
                    f"🕒 {posted}"
                )

            if description:

                with st.expander(
                    "📄 Job Description"
                ):

                    st.write(description)

        # =================================================
        # APPLY
        # =================================================

        with action_col:

            if apply_url:

                st.link_button(
                    "Apply Now →",
                    apply_url,
                    use_container_width=True,
                )

                share_text = f"{title} - {company}\n{apply_url}"
                whatsapp_url = f"https://wa.me/?text={quote(share_text)}"
                email_subject = quote(f"Job Opportunity: {title} - {company}")
                email_body = quote(share_text)
                email_url = f"mailto:?subject={email_subject}&body={email_body}"

                with st.popover("↗ Share", use_container_width=True):
                    st.link_button("WhatsApp", whatsapp_url, use_container_width=True)
                    st.link_button("Email", email_url, use_container_width=True)
                    st.code(apply_url, language=None)
                    st.caption("Copy the link above to share it anywhere else.")