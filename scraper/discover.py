"""discover: sitemap.xml -> Manifest entries (status: discovered).

Sitemaps are the file sites publish *for* crawlers — the politest discovery.
Handles both a flat urlset and a sitemap index of child sitemaps."""

from bs4 import BeautifulSoup

from . import manifest, politeness

SITEMAP_URL = "https://rationalreminder.ca/sitemap.xml"
EPISODE_PATH = "rationalreminder.ca/podcast/"


def _locs(xml_text: str) -> list[str]:
    soup = BeautifulSoup(xml_text, "xml")
    return [loc.text.strip() for loc in soup.find_all("loc")]


def is_episode_url(url: str) -> bool:
    if EPISODE_PATH not in url:
        return False
    tail = url.split(EPISODE_PATH, 1)[1].strip("/")
    return bool(tail)  # the collection page itself has an empty tail


def run() -> None:
    m = manifest.load()
    with politeness.make_client() as client:
        root = politeness.polite_get(client, SITEMAP_URL).text
        locs = _locs(root)
        child_sitemaps = [u for u in locs if u.endswith(".xml")]
        page_urls = [u for u in locs if not u.endswith(".xml")]
        for sm in child_sitemaps:
            politeness.pace()
            page_urls.extend(_locs(politeness.polite_get(client, sm).text))

    added = 0
    for url in page_urls:
        if not is_episode_url(url):
            continue
        slug = manifest.slug_of(url)
        if slug not in m:
            m[slug] = manifest.new_entry(url)
            added += 1
    manifest.save(m)
    total = len(m)
    print(f"discover: {added} new episode pages, {total} total in Manifest")
