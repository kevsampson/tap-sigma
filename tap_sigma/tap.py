"""Sigma Computing tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_sigma import streams


class TapSigma(Tap):
    """Sigma Computing tap class."""

    name = "tap-sigma"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=True,
            description="Sigma Computing API Client ID",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            secret=True,
            description="Sigma Computing API Client Secret",
        ),
        th.Property(
            "api_url",
            th.StringType,
            required=True,
            description=(
                "Base API URL for your Sigma Computing instance "
                "(e.g., https://aws-api.sigmacomputing.com)"
            ),
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [
            # Remove AccountTypesStream and FavoritesStream - not available in API
            streams.ConnectionsStream(self),
            streams.DatasetsStream(self),
            streams.MembersStream(self),
            streams.TeamsStream(self),
            streams.FilesStream(self),
            streams.WorkbooksStream(self),
            streams.WorkbookPagesStream(self),
            streams.TagsStream(self),
            streams.UserAttributesStream(self),
            streams.WhoAmIStream(self),
        ]


if __name__ == "__main__":
    TapSigma.cli()
