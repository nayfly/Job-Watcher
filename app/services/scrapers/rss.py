from typing import Any, Dict, List

import feedparser

from app.services.scrapers.base import Scraper


class RSSScraper(Scraper):
    def fetch(self, url: str) -> List[Dict[str, Any]]:
        feed = feedparser.parse(url)
        results: List[Dict[str, Any]] = []
        for entry in getattr(feed, "entries", []):
            # convert entry to dict; feedparser entries are objects with attributes
            item = {k: entry.get(k) for k in entry.keys()} if hasattr(entry, 'keys') else entry
            results.append(item)
        return results


# convenience function for simple use
_scraper = RSSScraper()

def fetch_feed(url: str) -> List[Dict[str, Any]]:
    return _scraper.fetch(url)
