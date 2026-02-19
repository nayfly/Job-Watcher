from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Scraper(ABC):
    """minimal interface for a job source scraper"""

    @abstractmethod
    def fetch(self, url: str) -> List[Dict[str, Any]]:
        """return a list of normalized job dictionaries"""
        ...
