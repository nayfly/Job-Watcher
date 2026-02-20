from typing import Any, Dict, List

from app.services.scrapers.base import Scraper


class RemoteOKScraper(Scraper):
    def fetch(self, url: str) -> List[Dict[str, Any]]:
        # remoteok has a JSON API; to keep MVP lean we just load it
        import httpx

        resp = httpx.get(url)
        resp.raise_for_status()
        data = resp.json()
        # assume data is a list of job records
        if isinstance(data, list):
            return data
        else:
            return []


# convenience
_scraper = RemoteOKScraper()


def fetch_remoteok(url: str) -> List[Dict[str, Any]]:
    return _scraper.fetch(url)
