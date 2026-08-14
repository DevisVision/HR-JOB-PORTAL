from services.aggregators.technopark import _parse_detail, _is_expired

HTML = """
<html><body>
SE-Mentor Solutions (P) Ltd
2nd Floor, Gayathri Building, Technopark Campus Trivandrum, Kerala, India , 695581
http://www.se-mentor.com
# Data Engineer
Closing Date:24,July 2026
Job Published: 17,July 2026
Contact Email: careers@se-mentor.com
Brief Description
We are hiring a Data Engineer with Snowflake and SQL.
Preferred Skills
Advanced SQL Queries
</body></html>
"""

def test_parse_technopark_detail():
    job = _parse_detail(HTML, "https://technopark.in/job-details/31537?job=Data+Engineer")
    assert job["title"] == "Data Engineer"
    assert job["company"] == "SE-Mentor Solutions (P) Ltd"
    assert job["posted_date"] == "17,July 2026"
    assert job["closing_date"] == "24,July 2026"
    assert "Snowflake" in job["skills"]



def test_parse_technopark_ust_detail():
    html = """
    <html><body>
    UST
    Bhavani , Technopark Phase I Technopark Rd, Technopark Campus 695581 , 695581
    http://www.ust.com
    # React Frontend
    Closing Date:17,Aug 2026
    Job Published: 03,July 2026
    Contact Email: praveenraja.TR@ust.com
    Brief Description
    Senior Front-End Developer for UST.
    Preferred Skills
    React, Node.js, PostgreSQL
    </body></html>
    """
    job = _parse_detail(
        html,
        "https://technopark.in/job-details/31152?job=React+Frontend",
    )
    assert job["title"] == "React Frontend"
    assert job["company"] == "UST"
    assert job["posted_date"] == "03,July 2026"
    assert job["closing_date"] == "17,Aug 2026"
