"""
=========================================================
VisionBoard Career Portal
Professional Search & Filters
=========================================================
"""

import streamlit as st


# =========================================================
# FILTERS
# =========================================================

def show_filters():

    st.markdown(
        """
        <div style="
        background:white;
        padding:18px;
        border-radius:16px;
        border:1px solid #E5E7EB;
        box-shadow:0 4px 12px rgba(0,0,0,.05);
        margin-bottom:20px;">

        <h3 style="
        margin:0;
        color:#0F4C81;">
        🔍 Find Your Next Career Opportunity
        </h3>

        <p style="
        margin-top:5px;
        color:#64748B;">
        Search jobs from Fortune 500 companies and leading employers.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # SEARCH
    # =====================================================

    search = st.text_input(
        "Search Job Title / Skill / Company",
        placeholder="Python, Spark, Azure, GenAI, IBM, Accenture...",
    )

    # =====================================================
    # FILTERS
    # =====================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        country = st.selectbox(
            "Country",
            [
                "All",
                "India",
                "Remote",
                "United States",
                "United Kingdom",
                "Germany",
                "Canada",
                "Australia",
                "Singapore",
                "UAE",
            ],
        )

    with c2:

        employment = st.selectbox(
            "Employment Type",
            [
                "All",
                "Full Time",
                "Contract",
                "Internship",
                "Part Time",
                "Temporary",
            ],
        )

    with c3:

        experience = st.selectbox(
            "Experience",
            [
                "All",
                "Fresher",
                "0-2 Years",
                "3-5 Years",
                "5-8 Years",
                "8+ Years",
            ],
        )

    with c4:

        sort = st.selectbox(
            "Sort By",
            [
                "Recommended",
                "Latest Jobs",
                "India First",
                "Remote First",
                "Company A-Z",
            ],
        )

    # =====================================================
    # SECOND ROW
    # =====================================================

    c5, c6, c7, c8 = st.columns(4)

    with c5:

        work_mode = st.selectbox(
            "Work Mode",
            [
                "All",
                "Remote",
                "Hybrid",
                "Onsite",
            ],
        )

    with c6:

        company = st.selectbox(
            "Top Companies",
            [
                "All",
                "IBM",
                "Accenture",
                "UST",
                "EY",
                "KPMG",
                "Capgemini",
                "Cisco",
                "Wipro",
                "Cognizant",
                "Tech Mahindra",
                "Allianz",
                "Microsoft",
                "Google",
                "Amazon",
                "Oracle",
                "TCS",
                "Infosys",
                "HCL",
            ],
        )

    with c7:

        posted = st.selectbox(
            "Posted Within",
            [
                "Any Time",
                "Today",
                "Last 3 Days",
                "Last 7 Days",
                "Last 30 Days",
            ],
        )

    with c8:

        salary = st.selectbox(
            "Salary",
            [
                "Any",
                "$20K+",
                "$40K+",
                "$60K+",
                "$80K+",
                "$100K+",
            ],
        )

    # =====================================================
    # QUICK FILTERS
    # =====================================================

    st.markdown("### Quick Filters")

    q1, q2, q3, q4, q5 = st.columns(5)

    with q1:
        india_only = st.checkbox("🇮🇳 India Jobs")

    with q2:
        remote_only = st.checkbox("🌍 Remote")

    with q3:
        fortune_only = st.checkbox("⭐ Fortune 500")

    with q4:
        freshers = st.checkbox("🎓 Freshers")

    with q5:
        verified = st.checkbox("✔ Verified")

    st.divider()

    return (
        search,
        country,
        employment,
        experience,
        sort,
        work_mode,
        company,
        posted,
        salary,
        india_only,
        remote_only,
        fortune_only,
        freshers,
        verified,
    )