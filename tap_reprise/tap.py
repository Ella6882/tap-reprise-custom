"""Reprise tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_reprise import streams


class TapReprise(Tap):
    """Reprise tap class."""

    name = "tap-reprise"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The client ID to authenticate against the API service. This is required for the Replay API.",
        ),
        th.Property(
            "replay_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the Replay API service",
        ),
        th.Property(
            "replicate_token",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The token to authenticate against the Replicate API service",
        ),
        th.Property(
            "start_timestamp",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
        th.Property(
            "end_timestamp",
            th.DateTimeType,
            description="The latest record date to sync",
        ),
        th.Property(
            "api_url",
            th.StringType,
            default="https://api.us-east.tinybird.co/v0/pipes/",
            description="The url for the API service",  
        ),
        th.Property(
            "domain",
            th.StringType,
            description="The domain for the company account.",  
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.RepriseStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ReplaySessionActivityDailyStream(self),
            #streams.ReplicateAnalyticsDailyStream(self),
        ]


if __name__ == "__main__":
    TapReprise.cli()
