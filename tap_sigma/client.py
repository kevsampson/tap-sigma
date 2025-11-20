"""REST client handling for Sigma Computing API streams."""

from typing import Any, Dict, Optional, Iterable
from urllib.parse import urljoin

import requests
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

from tap_sigma.auth import SigmaAuthenticator


class SigmaPaginator(BaseAPIPaginator):
    """Paginator for Sigma Computing API."""

    def __init__(self, start_value: int = 0, page_size: int = 100) -> None:
        """Initialize paginator.

        Args:
            start_value: Starting offset value.
            page_size: Number of records per page.
        """
        super().__init__(start_value)
        self._page_size = page_size
        self._finished = False

    def has_more(self, response: requests.Response) -> bool:
        """Check if more pages exist.

        Args:
            response: API response.

        Returns:
            True if more pages exist.
        """
        if self._finished:
            return False

        data = response.json()

        # Check if we got a full page of results
        if isinstance(data, dict):
            # For responses with 'entries' key
            entries = data.get("entries", [])
            if len(entries) < self._page_size:
                self._finished = True
                return False
            return True
        elif isinstance(data, list):
            # For direct list responses
            if len(data) < self._page_size:
                self._finished = True
                return False
            return True

        self._finished = True
        return False

    def get_next(self, response: requests.Response) -> Optional[int]:
        """Get next page offset.

        Args:
            response: API response.

        Returns:
            Next offset value or None.
        """
        if not self.has_more(response):
            return None

        return self.current_value + self._page_size


class SigmaStream(RESTStream):
    """Base stream class for Sigma Computing API."""

    @property
    def url_base(self) -> str:
        """Return the base URL for the API."""
        api_url = self.config.get("api_url", "").rstrip("/")
        return api_url

    @property
    def authenticator(self) -> SigmaAuthenticator:
        """Return authenticator instance."""
        auth_endpoint = urljoin(self.url_base, "/v2/auth/token")
        return SigmaAuthenticator(stream=self, auth_endpoint=auth_endpoint)

    @property
    def http_headers(self) -> Dict[str, str]:
        """Return standard HTTP headers.

        Returns:
            Dictionary of headers.
        """
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def get_new_paginator(self) -> SigmaPaginator:
        """Get a new paginator instance.

        Returns:
            A new paginator.
        """
        return SigmaPaginator(start_value=0, page_size=100)

    def get_url_params(
        self,
        context: Optional[Dict] = None,
        next_page_token: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get URL query parameters.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Pagination token.

        Returns:
            Dictionary of query parameters.
        """
        params: Dict[str, Any] = {}

        # Add pagination parameters if supported
        if next_page_token is not None:
            params["offset"] = next_page_token
            params["limit"] = 100

        return params

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse API response and yield records.

        Args:
            response: API response.

        Yields:
            Record dictionaries.
        """
        data = response.json()

        # Handle different response formats
        if isinstance(data, dict):
            # Check for 'entries' key (common in Sigma API)
            if "entries" in data:
                yield from data["entries"]
            # Check for other common list keys
            elif any(key in data for key in ["data", "results", "items"]):
                for key in ["data", "results", "items"]:
                    if key in data:
                        yield from data[key]
                        break
            # Single object response
            else:
                yield data
        elif isinstance(data, list):
            # Direct list response
            yield from data

    def backoff_wait_generator(self):
        """Generate wait times for backoff with jitter.

        Yields:
            Wait time in seconds.
        """
        # Start with 1 second and double each time, up to 60 seconds
        wait_time = 1
        while True:
            yield wait_time
            wait_time = min(wait_time * 2, 60)

    def backoff_max_tries(self) -> int:
        """Maximum number of retry attempts.

        Returns:
            Max retry count.
        """
        return 5
