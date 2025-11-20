"""Tests for tap-sigma core functionality."""

import pytest
from singer_sdk.testing import get_tap_test_class

from tap_sigma.tap import TapSigma

# Configuration for testing
SAMPLE_CONFIG = {
    "client_id": "test-client-id",
    "client_secret": "test-client-secret",
    "api_url": "https://aws-api.sigmacomputing.com",
}


# Run standard tap tests from the SDK
TestTapSigma = get_tap_test_class(
    tap_class=TapSigma,
    config=SAMPLE_CONFIG,
)


class TestTapSigmaCustom:
    """Custom tests for tap-sigma."""

    def test_tap_initialization(self):
        """Test that the tap can be initialized with config."""
        tap = TapSigma(config=SAMPLE_CONFIG)
        assert tap.name == "tap-sigma"
        assert tap.config["client_id"] == "test-client-id"

    def test_stream_discovery(self):
        """Test that all expected streams are discovered."""
        tap = TapSigma(config=SAMPLE_CONFIG)
        streams = tap.discover_streams()

        expected_streams = [
            "account_types",
            "connections",
            "datasets",
            "data_models",
            "members",
            "teams",
            "files",
            "workbooks",
            "workbook_pages",
            "favorites",
            "tags",
            "user_attributes",
            "whoami",
        ]

        discovered_stream_names = [stream.name for stream in streams]

        for expected_stream in expected_streams:
            assert (
                expected_stream in discovered_stream_names
            ), f"Stream {expected_stream} not discovered"

    def test_required_config_keys(self):
        """Test that required config keys are validated."""
        with pytest.raises(Exception):
            # Should fail without required config
            TapSigma(config={})
