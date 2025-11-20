"""Authentication handler for Sigma Computing API."""

import time
from typing import Any, Dict, Optional

import requests
from singer_sdk.authenticators import OAuthAuthenticator
from singer_sdk.streams import Stream as RESTStreamBase


class SigmaAuthenticator(OAuthAuthenticator):
    """Authenticator for Sigma Computing API using OAuth 2.0 client credentials."""

    def __init__(
        self,
        stream: RESTStreamBase,
        auth_endpoint: str,
        oauth_scopes: Optional[str] = None,
    ) -> None:
        """Initialize authenticator.

        Args:
            stream: The stream instance to authenticate for.
            auth_endpoint: The OAuth endpoint for token requests.
            oauth_scopes: Optional OAuth scopes.
        """
        super().__init__(stream=stream, auth_endpoint=auth_endpoint)
        self._tap = stream._tap
        self._token_expires_at: Optional[float] = None

    @property
    def oauth_request_body(self) -> Dict[str, Any]:
        """Return request body for OAuth request.

        Returns:
            Dictionary with OAuth request body.
        """
        return {
            "grant_type": "client_credentials",
            "client_id": self.config.get("client_id"),
            "client_secret": self.config.get("client_secret"),
        }

    def update_access_token(self) -> None:
        """Update the access token and store expiration time."""
        request_time = time.time()

        # Make the token request - Sigma API expects form data, not JSON
        token_response = requests.post(
            self.auth_endpoint,
            data=self.oauth_request_body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        try:
            token_response.raise_for_status()
        except requests.HTTPError as ex:
            msg = f"Failed to get access token: {token_response.text}"
            raise RuntimeError(msg) from ex

        token_json = token_response.json()
        self.access_token = token_json.get("access_token")

        # Sigma tokens expire after 1 hour (3600 seconds)
        # Set expiration slightly earlier to refresh before actual expiration
        expires_in = token_json.get("expires_in", 3600)
        self._token_expires_at = request_time + expires_in - 300  # 5 min buffer

        self.logger.info("Successfully obtained new access token")

    @property
    def is_token_valid(self) -> bool:
        """Check if token exists and is not expired.

        Returns:
            True if token is valid, False otherwise.
        """
        if not self.access_token:
            return False

        if self._token_expires_at is None:
            return False

        return time.time() < self._token_expires_at

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Authenticate the request.

        Args:
            request: The request to authenticate.

        Returns:
            The authenticated request.
        """
        # Refresh token if needed
        if not self.is_token_valid:
            self.update_access_token()

        # Add bearer token to request
        request.headers["Authorization"] = f"Bearer {self.access_token}"
        return request
