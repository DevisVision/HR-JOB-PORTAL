"""
=========================================================
VisionBoard Career Portal
Preferred Companies
=========================================================
Target companies used for:

• Ranking
• Priority display
• Company filters
• Homepage highlights
=========================================================
"""

# =========================================================
# Big Tech
# =========================================================

BIG_TECH = {

    "Microsoft",
    "Google",
    "Amazon",
    "Apple",
    "Meta",
    "Netflix",
    "IBM",
    "Oracle",
    "Cisco",
    "SAP",
    "Adobe",
    "NVIDIA",
    "Intel",
    "AMD",
    "Qualcomm",
    "Dell",
    "HP",
    "Lenovo",
    "Salesforce",
    "ServiceNow",
    "Snowflake",
    "Atlassian",
    "VMware",
    "Red Hat",
    "Broadcom",
}

# =========================================================
# Consulting
# =========================================================

CONSULTING = {

    "Accenture",
    "Capgemini",
    "Cognizant",
    "EY",
    "Deloitte",
    "PwC",
    "KPMG",
    "Infosys Consulting",
    "BearingPoint",
    "Slalom",
}

# =========================================================
# Indian IT Services
# =========================================================

INDIAN_IT = {

    "TCS",
    "Infosys",
    "Wipro",
    "HCL",
    "Tech Mahindra",
    "UST",
    "LTIMindtree",
    "Mphasis",
    "Persistent",
    "Hexaware",
    "Birlasoft",
    "Coforge",
    "L&T Technology Services",
    "Cyient",
    "KPIT",
    "Sonata Software",
    "Zensar",
    "Virtusa",
    "ValueLabs",
}

# =========================================================
# Banking & Financial Services
# =========================================================

BANKING = {

    "JPMorgan Chase",
    "Goldman Sachs",
    "Morgan Stanley",
    "Bank of America",
    "Citibank",
    "HSBC",
    "Barclays",
    "Standard Chartered",
    "American Express",
    "Wells Fargo",
    "BNY",
    "Mastercard",
    "Visa",
}

# =========================================================
# Insurance
# =========================================================

INSURANCE = {

    "Allianz",
    "AIG",
    "Prudential",
    "MetLife",
    "AXA",
    "Zurich",
}

# =========================================================
# Telecom
# =========================================================

TELECOM = {

    "Nokia",
    "Ericsson",
    "Vodafone",
    "AT&T",
    "Verizon",
}

# =========================================================
# Manufacturing / Industrial
# =========================================================

INDUSTRIAL = {

    "Bosch",
    "Siemens",
    "Schneider Electric",
    "ABB",
    "GE",
    "Honeywell",
    "Philips",
    "3M",
}

# =========================================================
# Cloud & AI
# =========================================================

CLOUD_AI = {

    "OpenAI",
    "Databricks",
    "MongoDB",
    "Elastic",
    "HashiCorp",
    "Confluent",
    "Cloudflare",
}

# =========================================================
# Fortune 500 (Priority Companies)
# =========================================================

FORTUNE_PRIORITY = (

    BIG_TECH
    | CONSULTING
    | INDIAN_IT
    | BANKING
    | INSURANCE
    | TELECOM
    | INDUSTRIAL
    | CLOUD_AI

)

# =========================================================
# Priority Score
# =========================================================

COMPANY_PRIORITY = {

    company: 100

    for company in FORTUNE_PRIORITY

}

# =========================================================
# Helper Functions
# =========================================================

def is_preferred_company(company: str) -> bool:

    if not company:
        return False

    return company.strip() in FORTUNE_PRIORITY


def get_company_priority(company: str) -> int:

    if not company:
        return 0

    return COMPANY_PRIORITY.get(company.strip(), 0)


def get_all_preferred_companies():

    return sorted(FORTUNE_PRIORITY)