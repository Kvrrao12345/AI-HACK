import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from rapidfuzz import fuzz

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}

KEYWORDS = [
    "about",
    "contact",
    "services",
    "solutions",
    "products",
    "company",
    "industries",
    "who-we-are",
    "what-we-do"
]

IGNORE = [
    "blog",
    "news",
    "press",
    "privacy",
    "terms",
    "cookie",
    "login",
    "signup",
    "career",
    "jobs",
    "release"
]

def fetch_page(url):
    """
    Download a webpage and return BeautifulSoup object.
    """
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        response.raise_for_status()

        return BeautifulSoup(response.text, "lxml")

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def clean_text(soup):
    """
    Remove unnecessary HTML and return readable text.
    """

    if soup is None:
        return ""

    for tag in soup([
        "script",
        "style",
        "nav",
        "header",
        "footer",
        "noscript",
        "svg",
        "form"
    ]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    return " ".join(text.split())


def get_internal_links(base_url, soup):
    """
    Extract internal links from homepage.
    """

    links = set()

    if soup is None:
        return []

    domain = urlparse(base_url).netloc

    for a in soup.find_all("a", href=True):

        href = a["href"]

        full = urljoin(base_url, href)

        if urlparse(full).netloc == domain:
            links.add(full)

    return list(links)

def find_relevant_links(links):

    selected = []

    for link in links:

        lower = link.lower()

        if any(word in lower for word in IGNORE):
            continue

        for keyword in KEYWORDS:

            score = fuzz.partial_ratio(lower, keyword)

            if score >= 80:
                selected.append(link)
                break

    return list(set(selected))[:5]

from extractor import extract_emails, extract_phones

def scrape_company(url):
    """
    Scrape homepage + relevant pages and return cleaned text.
    """

    homepage = fetch_page(url)

    if homepage is None:
        return None

    links = get_internal_links(url, homepage)

    relevant_links = find_relevant_links(links)

    pages = {}

    combined_text = ""

    # Add homepage text
    homepage_text = clean_text(homepage)
    combined_text += homepage_text[:3000] + "\n"
    # Visit relevant pages
    for link in relevant_links:

        soup = fetch_page(link)

        if soup:

            text = clean_text(soup)

            pages[link] = text[:500]

            combined_text += text[:3000] + "\n"

    emails = extract_emails(combined_text)

    phones = extract_phones(combined_text)

    return {
        "homepage": url,
        "pages": pages,
        "text": combined_text,
        "emails": emails,
        "phones": phones
    }