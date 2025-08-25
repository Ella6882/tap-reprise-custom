"""Stream type classes for tap-reprise."""

from __future__ import annotations

import sys
import re
from datetime import datetime, timezone
from importlib import resources
import typing as t
from tap_reprise.client import RepriseStream


if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

SCHEMAS_DIR = importlib_resources.files(__package__) / "schemas"

class ReplaySessionActivityDailyStream(RepriseStream):
    """Replay Session Activity stream from the Replay Data API."""

    name = "replay_session_activity_daily"
    path = ""
    primary_keys = ["activity_id"]
    replication_key = "create_at"
    schema_filepath = SCHEMAS_DIR / "replay_session_activity.json"

    def is_timestamp_replication_key(self) -> bool:
        return True

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:

        params = {}

        if next_page_token:
            params["offset"] = next_page_token

        replication_key = self.get_starting_timestamp(context)

        if replication_key is None:
            start_date = self.start_date
        else:
            start_date = replication_key.strftime("%Y-%m-%d %H:%M:%S")

        self.logger.info("Fetching %s → %s", start_date, self.end_date)

        params.update({
            "client_id": self.config["client_id"],
            "start_timestamp": start_date,
            "end_timestamp": self.end_date,
            "visitor_company": 1,
            "token": self.config["replay_token"],
            "limit": 250
        })
            
        return params

    def post_process(
        self,
        row: dict,
        context: Context | None = None,  # noqa: ARG002
    ) -> dict | None:
        """Modifies an individual record from a data stream 
            by obfuscating certain parts of the text, as required.

        Args:
            row: An individual record from the stream.
            context: The stream context.

        Returns:
            The updated record dictionary, or ``None`` to skip the record.
        """
        
        domain = self.config.get("domain", None)
        email = row.get('visitor_email')

        if email is not None and domain is not None:
            pattern = rf'^[\w\.-]+@({re.escape(domain)}\.\w+)$'
            match = re.match(pattern, email)
            if match:
                row['visitor_email'] = f"@{match.group(1)}"
            else:
                row['visitor_email'] = None

        return row

class ReplicateAnalyticsDailyStream(RepriseStream):
    """Replay Session Activity stream from the Replicate Data API."""

    name = "replicate_analytics_daily"
    path = ""
    primary_keys = ["shard_name"]
    replication_key = "session_date"
    schema_filepath = SCHEMAS_DIR / "replicate_analytics.json"

    def is_timestamp_replication_key(self) -> bool:
        return True

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:

        params = {}

        replication_key = self.get_starting_timestamp(context)

        if replication_key is None:
            start_date = self.start_date
        else:
            start_date = replication_key.strftime("%Y-%m-%d %H:%M:%S")
 
        self.logger.info("Fetching %s → %s", start_date, self.end_date)

        params.update({
            "start_timestamp": start_date,
            "end_timestamp": self.end_date,
            "token": self.config["replicate_token"]
        })
            
        return params