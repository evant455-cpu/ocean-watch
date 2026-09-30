"""Run settings and API-token handling. The token is never stored in code or in git."""

from __future__ import annotations

import getpass
import os
from dataclasses import dataclass
from pathlib import Path

TOKEN_ENV = "GFW_API_ACCESS_TOKEN"
CREDIT = "Data: Global Fishing Watch"


@dataclass(frozen=True)
class RunConfig:
    """Everything that can change between runs. Defaults reproduce the first analysis
    (Russian EEZ, Jan-Apr 2022, region id 5690 from the GFW guide)."""

    region_dataset: str = "public-eez-areas"   # also: MPAs, RFMOs (see GFW References API)
    region_id: str = "5690"
    start_date: str = "2022-01-01"
    end_date: str = "2022-05-01"
    max_gap_hours: float = 72.0                # "short gap" = shorter than this
    gap_limit: int = 100                       # gap events to pull (lower to 20 if the API complains)
    page_size: int = 100                       # rows per page when paging through events
    max_pages: int = 60                        # safety cap on paging (60 x 100 rows)
    out_dir: Path = Path("output")

    @property
    def region(self) -> dict:
        return {"dataset": self.region_dataset, "id": self.region_id}


def get_token(env_file: Path | None = None) -> str:
    """Find the GFW token: environment variable, then a .env file, then a hidden prompt."""
    token = os.environ.get(TOKEN_ENV, "").strip()
    if token:
        return token

    env_file = env_file or Path(".env")
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{TOKEN_ENV}="):
                token = line.split("=", 1)[1].strip().strip('"').strip("'")
                if token:
                    return token

    return getpass.getpass("Paste your GFW API token (hidden as you type): ").strip()
