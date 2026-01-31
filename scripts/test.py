import os

import fandom
import requests
from bs4 import BeautifulSoup

WIKI_NAME = "wot"
LANGUAGE = "en"
MAX_RESULTS = 5


def scrape_page_text(url: str) -> str:
    r = requests.get(url, timeout=30, headers={"User-Agent": "mw-scraper/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Wikipedia-style content container (often works on MediaWiki)
    content = soup.select_one("#mw-content-text")
    if not content:
        return ""

    # Remove reference markers/superscripts (optional)
    for sup in content.select("sup.reference"):
        sup.decompose()

    return content.get_text("\n", strip=True)


print(scrape_page_text("https://en.wikipedia.org/wiki/MediaWiki")[:500])

fandom.set_wiki(WIKI_NAME)
fandom.set_lang(LANGUAGE)
fandom.set_rate_limiting(True, min_wait=100)
fandom.set_user_agent("wheel-of-time-api/collect_character_pages")

query = "Biographical Information"

fandom.search(query, results=MAX_RESULTS)


results = fandom.search(query, results=MAX_RESULTS)
print(f"\nQuery: {query} ({len(results)} results)")
for title, _page_id in results:
    print(f"> {title}")
    page = fandom.page(title)
    print(f"> {title}")
    print(f"URL: {page.url}")

    page = scrape_page_text(page.url)

    # Save page content to a text file as html
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)
    filename = f"data/wiki_pages/{safe_title}.txt"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page)
