from abc import ABC, abstractmethod
from typing import Dict, Any, List

class JobSourceAdapter(ABC):
    @abstractmethod
    async def search_jobs(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search jobs based on parameters and return normalized job dictionaries."""
        pass

    @abstractmethod
    async def get_job_details(self, url: str) -> Dict[str, Any]:
        """Fetch details for a single job from a given URL."""
        pass

    @abstractmethod
    def normalize_job(self, raw_job: Any) -> Dict[str, Any]:
        """Normalize raw scraped job data into the standard dictionary format."""
        pass

    @abstractmethod
    def validate_source(self) -> bool:
        """Validate if scraping this source is permitted based on current rules/robots.txt."""
        pass
