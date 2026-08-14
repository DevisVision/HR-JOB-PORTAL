"""Technopark job collector for VisionBoard V5.

FINAL V5 FIX
------------
Technopark's detail page has a reliable structure:

    < All Jobs
    COMPANY
    company address
    company website
    # JOB TITLE
    Closing Date: ...
    Job Published: ...

The collector now extracts the employer from the company link/heading
associated with the detail page instead of guessing from navigation text.
This prevents values such as "Menu" and "Technopark Job Posting For ..."
from being stored as employers.

The collector intentionally keeps ALL active Technopark postings. Company
searches (UST, IBS, PITS, or any other company) are handled by the portal.
"""

import re
from datetime import date, datetime
from html import unescape
from html.parser import HTMLParser
from urllib.parse import parse_qs, unquote, urljoin, urlparse

import requests


BASE_URL = "https://technopark.in"
CRAWL_URL = f"{BASE_URL}/job-crawl"
SEARCH_URL = f"{BASE_URL}/job-search"
TIMEOUT = 25

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/151.0 Safari/537.36 "
        "VisionBoard Career Portal"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "*/*;q=0.8"
    ),
}


class _LinkParser(HTMLParser):
    """Collect anchor text/href in document order."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            self._href = dict(attrs).get("href") or ""
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            text = _clean_text(" ".join(self._text))
            self.links.append((text, self._href))
            self._href = None
            self._text = []


class _TextParser(HTMLParser):
    """Convert HTML into stable block-separated text."""

    BLOCK_TAGS = {
        "address", "article", "aside", "blockquote", "br", "div", "dl",
        "dt", "dd", "fieldset", "footer", "form", "h1", "h2", "h3",
        "h4", "h5", "h6", "header", "hr", "li", "main", "nav",
        "ol", "p", "pre", "section", "table", "tbody", "td", "th",
        "thead", "tr", "ul",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._skip_depth = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
            return
        if not self._skip_depth and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if not self._skip_depth and tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip_depth:
            for piece in re.split(r"\r?\n+", str(data or "")):
                value = _clean_text(piece)
                if value:
                    self.parts.append(value)


def _clean_text(value):
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def _fetch(session, url, params=None):
    response = session.get(
        url,
        params=params,
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.text


def _absolute_job_url(href):
    href = unquote(unescape(str(href or "").strip()))
    if not href:
        return ""

    absolute = urljoin(BASE_URL, href).split("#", 1)[0]
    parsed = urlparse(absolute)

    if parsed.netloc.lower() != urlparse(BASE_URL).netloc.lower():
        return ""

    if "/job-details/" not in parsed.path.lower():
        return ""

    return absolute


def _detail_id(url):
    match = re.search(r"/job-details/(\d+)", urlparse(url).path, re.I)
    return match.group(1) if match else ""


def _title_from_url(url):
    params = parse_qs(urlparse(url).query)
    return _clean_text(unquote(params.get("job", [""])[0]))


def _parse_date(value):
    value = _clean_text(value)
    if not value:
        return None

    for fmt in (
        "%d,%B %Y",
        "%d, %B %Y",
        "%d,%b %Y",
        "%d, %b %Y",
        "%d,%B,%Y",
        "%d, %B, %Y",
    ):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def _extract_date(text, label):
    pattern = (
        rf"{re.escape(label)}\s*:\s*"
        rf"(\d{{1,2}}\s*,?\s*[A-Za-z]+\s+\d{{4}})"
    )
    match = re.search(pattern, text, re.I)
    return _clean_text(match.group(1)) if match else ""


def _is_expired(closing_date):
    parsed = _parse_date(closing_date)
    return bool(parsed and parsed < date.today())


def _looks_like_bad_company(value):
    """Reject navigation/UI strings that are never employers."""
    value = _clean_text(value)
    low = value.casefold()

    if not value:
        return True

    if len(value) > 180:
        return True

    bad_exact = {
        "menu",
        "search",
        "job search",
        "all jobs",
        "< all jobs",
        "companies & jobs",
        "careers@technopark",
        "technopark",
    }

    if low in bad_exact:
        return True

    bad_prefixes = (
        "technopark job posting for",
        "posted on:",
        "job published:",
        "closing date:",
        "contact email:",
    )

    if low.startswith(bad_prefixes):
        return True

    if low.startswith(("http://", "https://", "www.")):
        return True

    if "@" in value:
        return True

    return False


def _extract_detail_company(html, title):
    """Extract the real employer from the detail-page header.

    On the live Technopark detail page, the company appears as a link
    immediately after '< All Jobs' and before the job title. Example:

        < All Jobs
        UST
        Bhavani, Technopark Phase I ...
        http://www.ust.com
        # Azure Data Engineer

    We use that structural relationship first. This is much more reliable
    than deriving a company from navigation text or the job title.
    """

    parser = _LinkParser()
    parser.feed(html)

    links = [
        (_clean_text(text), _clean_text(href))
        for text, href in parser.links
        if _clean_text(text)
    ]

    title_norm = _clean_text(title).casefold().lstrip("# ")

    # Find the first company-looking anchor after the "All Jobs" link.
    # The company link on Technopark currently points to the same
    # /job-details/... URL, so do not require a company-domain href.
    all_jobs_index = -1
    for index, (text, href) in enumerate(links):
        low = text.casefold()
        if "all jobs" in low or low.startswith("< all jobs"):
            all_jobs_index = index
            break

    candidates = []
    start = max(0, all_jobs_index + 1)

    for text, href in links[start:]:
        low = text.casefold()

        if title_norm and low.lstrip("# ") == title_norm:
            break

        if _looks_like_bad_company(text):
            continue

        if low in {"this is technopark", "companies & jobs",
                   "infrastructure & services", "happening here"}:
            continue

        # Skip common footer/navigation links.
        if any(
            token in low
            for token in (
                "company login",
                "visitor pass",
                "facility booking",
                "contact us",
                "space request",
                "privacy policy",
                "all news",
                "tenders",
                "events",
                "blog",
                "browse companies",
                "careers@technopark",
            )
        ):
            continue

        candidates.append(text)

        # The employer is the first valid item in this header region.
        if candidates:
            return candidates[0]

    # Strong fallback: derive a brand from Contact Email.
    email_match = re.search(
        r"Contact Email\s*:\s*([^\s<]+)",
        _html_to_text(html),
        re.I,
    )
    if email_match:
        domain = email_match.group(1).split("@", 1)[-1].lower()
        domain = domain.split(":", 1)[0].strip(".,;")
        generic = {
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "rediffmail.com", "protonmail.com", "icloud.com",
        }
        if domain not in generic:
            brand = domain.split(".")[0]
            known = {
                "ust": "UST",
                "ibs": "IBS",
                "pitsolutions": "PIT Solutions",
            }
            return known.get(brand, brand.replace("-", " ").title())

    return ""


def _html_to_text(html):
    parser = _TextParser()
    parser.feed(html)
    return _clean_text(" ".join(parser.parts))


def _extract_section(text, start, stops):
    pattern = (
        rf"{re.escape(start)}\s*(.*?)"
        rf"(?:{'|'.join(re.escape(s) for s in stops)}|$)"
    )
    match = re.search(pattern, text, re.I | re.S)
    return _clean_text(match.group(1)) if match else ""


def _parse_detail(html, url, link_title=""):
    text = _html_to_text(html)

    title = _title_from_url(url) or _clean_text(link_title)

    if not title:
        match = re.search(
            r"#\s*(.+?)\s+Closing Date\s*:",
            text,
            re.I,
        )
        title = _clean_text(match.group(1)) if match else ""

    published = _extract_date(text, "Job Published")
    closing = _extract_date(text, "Closing Date")

    company = _extract_detail_company(html, title)

    description = _extract_section(
        text,
        "Brief Description",
        (
            "Preferred Skills",
            "Additional Information",
            "Contact Email",
            "Happening Here",
        ),
    )

    skills = _extract_section(
        text,
        "Preferred Skills",
        (
            "Additional Information",
            "Contact Email",
            "Happening Here",
        ),
    )

    # Include the full detail text in skills/searchable content so a job such
    # as "Azure Data Engineer" is discoverable even if the preferred-skills
    # block is formatted unusually.
    combined_skills = _clean_text(
        " ".join(value for value in (description, skills) if value)
    )

    return {
        "job_id": f"technopark-{_detail_id(url) or url.rstrip('/').split('/')[-1]}",
        "title": title,
        "company": company,
        "location": "Technopark, Thiruvananthapuram, Kerala, India",
        "country": "India",
        "employment_type": "",
        "skills": combined_skills,
        "salary": "",
        "description": description or text,
        "source": "Technopark",
        "apply_url": url,
        "posted_date": published,
        "closing_date": closing,
    }


def _discover_links(html):
    parser = _LinkParser()
    parser.feed(html)

    jobs = {}
    for link_title, href in parser.links:
        url = _absolute_job_url(href)
        if not url:
            continue
        jobs[url] = _clean_text(link_title) or _title_from_url(url)

    return list(jobs.items())


def _discover_from_search(session, search_term="", start=None):
    try:
        params = {"type": "Job Posting"}

        if search_term:
            params["search"] = search_term

        if start is not None:
            params["start"] = start

        html = _fetch(session, SEARCH_URL, params=params)
        return _discover_links(html)

    except Exception as exc:
        label = f"{search_term or 'all jobs'} start={start}"
        print(
            f"Technopark search discovery skipped "
            f"[{label}]: {exc}"
        )
        return []


def _discover_search_pages(session, page_size=20, max_pages=50):
    discovered = {}

    for page in range(max_pages):
        start = page * page_size
        links = _discover_from_search(
            session,
            start=start,
        )

        if not links:
            break

        before = len(discovered)

        for url, title in links:
            discovered.setdefault(url, title)

        # Stop when pagination starts returning the same page repeatedly.
        if len(discovered) == before and page > 0:
            break

    return discovered


def fetch_technopark_jobs():
    """Return all active Technopark job postings with real employers."""

    session = requests.Session()
    session.headers.update(HEADERS)

    print("Fetching Technopark jobs...")

    crawl_html = _fetch(
        session,
        CRAWL_URL,
    )

    discovered = dict(
        _discover_links(crawl_html)
    )

    crawl_count = len(discovered)

    paginated = _discover_search_pages(
        session
    )

    for url, title in paginated.items():
        discovered.setdefault(url, title)

    # Keyword discovery is additive, not the primary source.
    try:
        from config.job_keywords import JOB_SEARCHES

        for keyword in JOB_SEARCHES:
            for url, title in _discover_from_search(
                session,
                search_term=keyword,
            ):
                discovered.setdefault(url, title)

    except Exception as exc:
        print(
            f"Technopark keyword discovery skipped: {exc}"
        )

    print(
        f"Technopark : {crawl_count} links from /job-crawl; "
        f"{len(paginated)} from paginated /job-search; "
        f"{len(discovered)} unique detail links after all discovery paths."
    )

    jobs = []
    expired = 0
    invalid = 0
    detail_failures = 0
    bad_company = 0

    for url, link_title in discovered.items():
        try:
            html = _fetch(
                session,
                url,
            )

            job = _parse_detail(
                html,
                url,
                link_title,
            )

            if not job.get("title") or not job.get("apply_url"):
                invalid += 1
                continue

            if not job.get("company"):
                bad_company += 1
                print(
                    f"Technopark company missing: "
                    f"{job.get('title')} -> {url}"
                )
                continue

            if _looks_like_bad_company(job["company"]):
                bad_company += 1
                print(
                    f"Technopark invalid company "
                    f"'{job['company']}': {url}"
                )
                continue

            if _is_expired(
                job.get("closing_date", "")
            ):
                expired += 1
                continue

            jobs.append(job)

        except Exception as exc:
            detail_failures += 1
            print(
                f"Technopark detail failed: "
                f"{url} -> {exc}"
            )

    # Stable source-level dedupe by Technopark job ID.
    unique = {}

    for job in jobs:
        unique[job["job_id"]] = job

    jobs = list(unique.values())

    print(
        "Technopark : "
        f"{len(jobs)} active jobs accepted | "
        f"expired={expired}, invalid={invalid}, "
        f"bad_company={bad_company}, "
        f"detail_failures={detail_failures}."
    )

    return jobs
