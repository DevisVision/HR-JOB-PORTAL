"""
=========================================================
VisionBoard Career Portal
Primary Search & Job Filter
components/filters.py
=========================================================
Client-facing simplified filter design
=========================================================
"""

import streamlit as st


# =========================================================
# FILTER COMPONENT
# =========================================================

def show_filters():

    # -----------------------------------------------------
    # Search Header
    # -----------------------------------------------------

    #st.markdown(
    #    """
    #    <div class="vb-search-header">

     #       <div class="vb-search-title">
     #           Find Your Next Career Opportunity
     #       </div>

     #       <div class="vb-search-subtitle">
      #          Search the latest opportunities from leading
      #          companies across India and worldwide.
       #     </div>

      #  </div>
      #3  """,
      #  unsafe_allow_html=True,
    #)

    #st.write("")


    # =====================================================
    # PRIMARY SEARCH
    # =====================================================

    search = st.text_input(
        "Search",
        placeholder=(
            "Search job title, skill, company, "
            "technology or location..."
        ),
        label_visibility="collapsed",
        key="primary_job_search",
    )


    # -----------------------------------------------------
    # Search Examples
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="vb-search-example">
            Examples: Python, PySpark, Azure Data Engineer,
            Databricks, IBM, Accenture, Bangalore
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")


    # =====================================================
    # JOB LOCATION / TYPE FILTER
    # =====================================================

    filter_value = st.radio(
        "Job Filter",
        [
            "All Jobs",
            "India",
            "Remote",
            "Abroad",
            "Verified Jobs",
        ],
        horizontal=True,
        index=0,
        key="job_location_filter",
    )


    # =====================================================
    # CONVERT RADIO FILTER
    # =====================================================

    india_only = filter_value == "India"

    remote_only = filter_value == "Remote"

    abroad_only = filter_value == "Abroad"

    verified_only = filter_value == "Verified Jobs"


    # =====================================================
    # SMALL DIVIDER
    # =====================================================

    st.markdown(
        """
        <div class="vb-filter-divider"></div>
        """,
        unsafe_allow_html=True,
    )


    # =====================================================
    # RETURN VALUES
    # =====================================================

    return (
        search,
        filter_value,
        india_only,
        remote_only,
        abroad_only,
        verified_only,
    )