"""
services/enrichment.py

Common enrichment for all job aggregators.
"""

import re


# =====================================================
# Priority
# =====================================================

INDIA_LOCATIONS = [

    "india",

    "bangalore",
    "bengaluru",

    "hyderabad",

    "chennai",

    "mumbai",

    "pune",

    "gurgaon",
    "gurugram",

    "noida",

    "delhi",
    "new delhi",

    "kolkata",

    "kochi",

    "trivandrum",
    "thiruvananthapuram",

    "ahmedabad",

    "jaipur",

    "coimbatore",

    "nagpur",

    "lucknow",

    "indore",

    "bhubaneswar",

    "visakhapatnam",

    "mysore"

]


def get_priority(job):
    """
    Priority

    1 = India
    2 = Remote
    3 = Global
    4 = Government
    """

    location = (job.get("location") or "").lower()

    country = (job.get("country") or "").lower()

    source = (job.get("source") or "").lower()

    text = f"{location} {country}"

    # ----------------------------------------
    # India Jobs
    # ----------------------------------------

    for city in INDIA_LOCATIONS:

        if city in text:

            return 1

    # ----------------------------------------
    # Remote Jobs
    # ----------------------------------------

    if any(
        word in text
        for word in [
            "remote",
            "work from home",
            "wfh",
            "anywhere"
        ]
    ):

        return 2

    # ----------------------------------------
    # Government Jobs
    # ----------------------------------------

    if source == "usajobs":

        return 4

    # ----------------------------------------
    # Everything Else
    # ----------------------------------------

    return 3


# =====================================================
# Work Mode
# =====================================================

def get_work_mode(job):
    """
    Detect work mode from multiple fields.
    """

    location = (job.get("location") or "").lower()

    employment = (job.get("employment_type") or "").lower()

    description = (job.get("description") or "").lower()

    text = f"{location} {employment} {description}"

    # ----------------------------------------
    # Remote
    # ----------------------------------------

    remote_keywords = [
        "remote",
        "work from home",
        "wfh",
        "anywhere",
        "distributed",
        "remote-first"
    ]

    if any(keyword in text for keyword in remote_keywords):
        return "Remote"

    # ----------------------------------------
    # Hybrid
    # ----------------------------------------

    hybrid_keywords = [
        "hybrid",
        "flexible",
        "split week"
    ]

    if any(keyword in text for keyword in hybrid_keywords):
        return "Hybrid"

    # ----------------------------------------
    # On-Site
    # ----------------------------------------

    onsite_keywords = [
        "on-site",
        "onsite",
        "office",
        "in office",
        "on premise"
    ]

    if any(keyword in text for keyword in onsite_keywords):
        return "On-Site"

    # ----------------------------------------
    # Unknown
    # ----------------------------------------

    return ""


# =====================================================
# Job Categories
# =====================================================

CATEGORY_RULES = {

    "Azure Data Engineering": [

        "azure data engineer",
        "azure synapse",
        "azure data factory",
        "adf",
        "azure databricks"

    ],

    "Data Engineering": [

        "data engineer",
        "etl",
        "spark",
        "pyspark",
        "databricks",
        "snowflake",
        "hadoop",
        "kafka",
        "airflow",
        "dbt"

    ],

    "Data Science": [

        "data scientist",
        "statistics",
        "analytics",
        "predictive",
        "forecasting"

    ],

    "Artificial Intelligence": [

        "artificial intelligence",
        "machine learning",
        "deep learning",
        "genai",
        "llm",
        "openai",
        "langchain",
        "rag",
        "prompt engineer",
        "ai engineer"

    ],

    "Software Engineering": [

        "software engineer",
        "software developer",
        "python developer",
        "java developer",
        "backend developer",
        "frontend developer",
        "full stack",
        "react",
        "angular",
        "node"

    ],

    "Cloud Engineering": [

        "azure",
        "aws",
        "amazon web services",
        "gcp",
        "google cloud",
        "cloud engineer"

    ],

    "DevOps": [

        "devops",
        "docker",
        "kubernetes",
        "terraform",
        "jenkins",
        "ci/cd"

    ],

    "Business Intelligence": [

        "power bi",
        "tableau",
        "qlik",
        "bi developer",
        "reporting"

    ],

    "Cyber Security": [

        "security",
        "cyber",
        "penetration",
        "soc analyst",
        "ethical hacker"

    ]
}


def get_job_category(job):
    """
    Detect the most appropriate job category.
    """

    text = " ".join(

        [

            job.get("title", ""),

            job.get("description", ""),

            job.get("skills", "")

        ]

    ).lower()

    for category, keywords in CATEGORY_RULES.items():

        for keyword in keywords:

            if keyword.lower() in text:

                return category

    return "Other"  


# =====================================================
# Company Logos
# =====================================================

COMPANY_LOGOS = {

    # Big Tech

    "microsoft": "https://logo.clearbit.com/microsoft.com",

    "google": "https://logo.clearbit.com/google.com",

    "amazon": "https://logo.clearbit.com/amazon.com",

    "meta": "https://logo.clearbit.com/meta.com",

    "apple": "https://logo.clearbit.com/apple.com",

    "netflix": "https://logo.clearbit.com/netflix.com",

    "openai": "https://logo.clearbit.com/openai.com",

    "anthropic": "https://logo.clearbit.com/anthropic.com",

    "nvidia": "https://logo.clearbit.com/nvidia.com",

    "oracle": "https://logo.clearbit.com/oracle.com",

    "ibm": "https://logo.clearbit.com/ibm.com",

    "intel": "https://logo.clearbit.com/intel.com",

    "cisco": "https://logo.clearbit.com/cisco.com",

    "salesforce": "https://logo.clearbit.com/salesforce.com",

    "adobe": "https://logo.clearbit.com/adobe.com",

    # Consulting

    "accenture": "https://logo.clearbit.com/accenture.com",

    "capgemini": "https://logo.clearbit.com/capgemini.com",

    "deloitte": "https://logo.clearbit.com/deloitte.com",

    "ey": "https://logo.clearbit.com/ey.com",

    "kpmg": "https://logo.clearbit.com/kpmg.com",

    "pwc": "https://logo.clearbit.com/pwc.com",

    # India

    "tcs": "https://logo.clearbit.com/tcs.com",

    "infosys": "https://logo.clearbit.com/infosys.com",

    "wipro": "https://logo.clearbit.com/wipro.com",

    "hcl": "https://logo.clearbit.com/hcltech.com",

    "tech mahindra": "https://logo.clearbit.com/techmahindra.com",

    "cognizant": "https://logo.clearbit.com/cognizant.com",

    "ltimindtree": "https://logo.clearbit.com/ltimindtree.com",

    "zoho": "https://logo.clearbit.com/zoho.com",

    "freshworks": "https://logo.clearbit.com/freshworks.com",

}


def get_company_logo(job):
    """
    Returns logo URL if company is known.
    """

    company = (
        job.get("company", "")
        .strip()
        .lower()
    )

    return COMPANY_LOGOS.get(company, "")


# =====================================================
# Enrich Job
# =====================================================

def enrich_job(job):

    job["priority"] = get_priority(job)

    job["work_mode"] = get_work_mode(job)

    job["job_category"] = get_job_category(job)

    job["company_logo"] = get_company_logo(job)

    job["is_active"] = 1

    return job