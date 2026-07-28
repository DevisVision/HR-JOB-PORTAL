"""
Central job relevance filter.

All aggregators use this filter before returning jobs.
"""

import re

# ==========================================================
# Positive Keywords
# ==========================================================

POSITIVE_KEYWORDS = [

    # Data Engineering
    "data engineer",
    "senior data engineer",
    "lead data engineer",
    "principal data engineer",
    "big data engineer",
    "etl",
    "etl developer",
    "data warehouse",
    "data platform",
    "data architect",

    # Analytics
    "data analyst",
    "analytics engineer",
    "business intelligence",
    "bi developer",

    # SQL
    "sql",
    "sql developer",
    "sql engineer",

    # Spark
    "spark",
    "pyspark",
    "apache spark",

    # Databricks
    "databricks",

    # Cloud
    "azure",
    "azure data engineer",
    "azure data factory",
    "azure synapse",
    "microsoft fabric",
    "fabric",
    "aws",
    "gcp",
    "snowflake",

    # Streaming
    "kafka",
    "streaming",

    # DevOps
    "azure devops",
    "devops engineer",

    # AI
    "ai engineer",
    "machine learning",
    "machine learning engineer",
    "ml engineer",
    "genai",
    "generative ai",
    "llm",
    "rag",
    "langchain",
    "openai",
    "prompt engineer",

    # Python
    "python",
    "python developer",
]

# ==========================================================
# Negative Job Titles
# ==========================================================

NEGATIVE_TITLES = [

    "doctor",
    "physician",
    "nurse",
    "medical",

    "dentist",
    "surgeon",

    "patient",

    "sales",
    "marketing",

    "recruiter",
    "recruitment",

    "human resources",
    "hr",

    "finance",
    "accountant",

    "teacher",
    "professor",

    "driver",

    "chef",
    "cook",
    "waiter",

    "mechanical engineer",
    "civil engineer",
    "electrical engineer",

    "customer support",

    "operations manager",
]

# ==========================================================
# Helper
# ==========================================================

def clean_text(text):

    text = text.lower()

    text = re.sub(r"<[^>]+>", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text


# ==========================================================
# Main Filter
# ==========================================================

def is_relevant_job(title="", description="", tags=""):

    title = clean_text(title)
    description = clean_text(description)
    tags = clean_text(tags)

    # ------------------------------------------------------
    # Reject ONLY if title itself is unrelated
    # ------------------------------------------------------

    for word in NEGATIVE_TITLES:

        if word in title:
            return False

    # ------------------------------------------------------
    # Strong match in TITLE
    # ------------------------------------------------------

    for word in POSITIVE_KEYWORDS:

        if word in title:
            return True

    # ------------------------------------------------------
    # Strong match in TAGS
    # ------------------------------------------------------

    for word in POSITIVE_KEYWORDS:

        if word in tags:
            return True

    # ------------------------------------------------------
    # Description fallback
    # Need at least TWO positive keywords
    # ------------------------------------------------------

    score = 0

    for word in POSITIVE_KEYWORDS:

        if word in description:
            score += 1

    if score >= 2:
        return True

    return False