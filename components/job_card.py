"""
=========================================================
VisionBoard Career Portal
Professional Job Card
=========================================================
"""

import streamlit as st


def show_job_card(job):

    # ---------------------------------------------------
    # Job Details
    # ---------------------------------------------------

    title = job.get("title", "Job Title")

    company = job.get("company", "Unknown Company")

    location = job.get("location", "Location Not Available")

    employment = job.get("employment_type", "Not Specified")

    work_mode = job.get("work_mode", "")

    salary = job.get("salary", "Not Disclosed")

    posted = str(job.get("posted_date", ""))[:10]

    source = job.get("source", "VisionBoard")

    description = job.get("description", "")

    apply_url = job.get("apply_url", "")

    company_logo = job.get("company_logo", "")

    skills = job.get("skills", "")

    country = job.get("country", "")

    priority = job.get("priority", 3)

    # ---------------------------------------------------
    # Badge
    # ---------------------------------------------------

    if priority == 1:
        badge = "🇮🇳 India"

    elif priority == 2:
        badge = "🏠 Remote"

    elif country:
        badge = f"🌍 {country}"

    else:
        badge = "🌎 Global"

    # ---------------------------------------------------
    # Skills
    # ---------------------------------------------------

    if isinstance(skills, str):

        skills = [
            x.strip()
            for x in skills.split(",")
            if x.strip()
        ]

    # ---------------------------------------------------
    # Description
    # ---------------------------------------------------

    if len(description) > 220:
        description = description[:220] + "..."

    # ---------------------------------------------------
    # Unique Key
    # ---------------------------------------------------

    unique_id = (
        job.get("job_id")
        or job.get("id")
        or f"{title}_{company}"
    )

    # ---------------------------------------------------
    # Card
    # ---------------------------------------------------

    with st.container(border=True):

        left, right = st.columns([1, 8])

        # -----------------------------------------------

        with left:

            if company_logo:

                st.image(
                    company_logo,
                    width=60,
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                        width:60px;
                        height:60px;
                        border-radius:50%;
                        background:#0F4C81;
                        color:white;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:24px;
                        font-weight:bold;
                    ">
                        {company[:1].upper()}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # -----------------------------------------------

        with right:

            st.markdown(
                f"### {title}"
            )

            st.caption(f"🏢 {company}")

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.caption(f"📍 {location}")

            with c2:

                if work_mode:

                    st.caption(f"🏠 {work_mode}")

                else:

                    st.caption(f"💼 {employment}")

            with c3:

                st.caption(f"💰 {salary}")

            with c4:

                st.caption(f"📅 {posted}")

            if skills:

                st.write(
                    " • ".join(skills[:6])
                )

            st.write(description)

            st.caption(
                f"{badge} | Source: {source}"
            )

        st.divider()

        # ---------------------------------------------------
        # Buttons
        # ---------------------------------------------------

        b1, b2, b3 = st.columns([2, 1, 1])

        with b1:

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
                    key=f"apply_{unique_id}",
                    use_container_width=True,
                )

        with b2:

            st.button(
                "⭐ Save",
                key=f"save_{unique_id}",
                use_container_width=True,
            )

        with b3:

            if apply_url:

                st.link_button(
                    "🔗 Share",
                    apply_url,
                    use_container_width=True,
                )

            else:

                st.button(
                    "🔗 Share",
                    disabled=True,
                    key=f"share_{unique_id}",
                    use_container_width=True,
                )

    st.write("")