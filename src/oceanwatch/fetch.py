"""All calls to the Global Fishing Watch API live here. Every function takes a client and a
RunConfig and returns a pandas DataFrame, so the rest of the package never touches the network."""

from __future__ import annotations

import pandas as pd

from oceanwatch.config import RunConfig

GAPS_DATASET = "public-global-gaps-events:latest"
ENCOUNTERS_DATASET = "public-global-encounters-events:latest"


async def fishing_effort(client, cfg: RunConfig) -> pd.DataFrame:
    """AIS apparent fishing effort, monthly, grouped by flag."""
    res = await client.fourwings.create_fishing_effort_report(
        spatial_resolution="LOW",
        temporal_resolution="MONTHLY",
        group_by="FLAG",
        start_date=cfg.start_date,
        end_date=cfg.end_date,
        region=cfg.region,
    )
    return res.df()


async def sar_detections(client, cfg: RunConfig) -> pd.DataFrame:
    """SAR (radar) vessel detections, monthly, grouped by flag. Blank flag = no AIS match."""
    res = await client.fourwings.create_sar_presence_report(
        spatial_resolution="LOW",
        temporal_resolution="MONTHLY",
        group_by="FLAG",
        start_date=cfg.start_date,
        end_date=cfg.end_date,
        region=cfg.region,
    )
    return res.df()


async def gap_events(client, cfg: RunConfig) -> pd.DataFrame:
    """AIS-gap events ("went dark") in the region."""
    res = await client.events.get_all_events(
        datasets=[GAPS_DATASET],
        start_date=cfg.start_date,
        end_date=cfg.end_date,
        region=cfg.region,
        limit=cfg.gap_limit,
    )
    return res.df()


async def encounter_events(client, cfg: RunConfig, vessel_ids: list[str] | None = None) -> pd.DataFrame:
    """Fishing-carrier encounters, paged. With vessel_ids, only those vessels (no region filter)."""
    pages, seen = [], set()
    for page in range(cfg.max_pages):
        kwargs = dict(
            datasets=[ENCOUNTERS_DATASET],
            encounter_types=["FISHING-CARRIER"],
            start_date=cfg.start_date,
            end_date=cfg.end_date,
            limit=cfg.page_size,
            offset=page * cfg.page_size,
        )
        if vessel_ids:
            kwargs["vessels"] = vessel_ids
        else:
            kwargs["region"] = cfg.region
        df = (await client.events.get_all_events(**kwargs)).df()
        if df is None or len(df) == 0:
            break
        new = df[~df["id"].isin(seen)]
        seen.update(new["id"].tolist())
        pages.append(new)
        print(f"  encounters page {page + 1}: {len(df)} rows, {len(new)} new")
        if len(df) < cfg.page_size or len(new) == 0:
            break
    else:
        print(f"WARNING: hit the {cfg.max_pages}-page cap; results may be incomplete.")
    return pd.concat(pages, ignore_index=True) if pages else pd.DataFrame()
