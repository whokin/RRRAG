"""Polite HTTP access to rationalreminder.ca — the only module that touches
the network. Politeness settings per PLAN.md: sequential, fixed delay, honest
UA, backoff on 5xx, immediate halt on 403/429."""

import time

import httpx

USER_AGENT = "RRRAG-scraper/0.1 (personal learning project; warrenhokin@gmail.com)"
DELAY_SECONDS = 2.0
MAX_RETRIES = 3
TIMEOUT = httpx.Timeout(30.0)


class BlockedError(Exception):
    """Got 403/429 — the site is telling us to stop. Reassess, never retry through it."""


class FetchError(Exception):
    """Non-block failure that survived retries."""


def make_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT,
        follow_redirects=True,
    )


def polite_get(client: httpx.Client, url: str) -> httpx.Response:
    """GET with retries on 5xx (exponential backoff) and hard stop on 403/429.

    Does NOT sleep the inter-request delay itself — callers own pacing so a
    single one-off request isn't needlessly delayed."""
    for attempt in range(MAX_RETRIES):
        response = client.get(url)
        if response.status_code in (403, 429):
            raise BlockedError(f"{response.status_code} from {url} — halting")
        if response.status_code >= 500:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2**attempt * 2)
                continue
            raise FetchError(f"{response.status_code} from {url} after {MAX_RETRIES} tries")
        response.raise_for_status()
        return response
    raise FetchError(f"unreachable: {url}")


def pace() -> None:
    """The fixed inter-request delay; called between requests in any loop."""
    time.sleep(DELAY_SECONDS)
