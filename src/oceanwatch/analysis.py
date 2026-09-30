"""Pure pandas analysis: no network, no plotting. Easy to test with fake data."""

from __future__ import annotations

import pandas as pd


def unidentified_share(sar_df: pd.DataFrame):
    """(dark_rows, dark_total, all_total, percent) for SAR detections with no flag (no AIS match)."""
    dark = sar_df[sar_df["flag"].fillna("") == ""]
    dark_total = int(dark["detections"].sum())
    all_total = int(sar_df["detections"].sum())
    pct = round(100 * dark_total / all_total, 1) if all_total else 0.0
    return dark, dark_total, all_total, pct


def flatten_gaps(gap_events_df: pd.DataFrame) -> pd.DataFrame:
    """Unpack the nested 'vessel' and 'gap' columns into ordinary columns (v_*, g_*)."""
    v = pd.json_normalize(gap_events_df["vessel"].tolist()).add_prefix("v_")
    g = pd.json_normalize(gap_events_df["gap"].tolist()).add_prefix("g_")
    base = gap_events_df[["start", "end"]].reset_index(drop=True)
    out = pd.concat([base, v, g], axis=1)
    if "g_duration_hours" in out.columns:
        out["g_duration_hours"] = pd.to_numeric(out["g_duration_hours"], errors="coerce")
    return out


def short_fishing_gaps(flat: pd.DataFrame, max_hours: float) -> pd.DataFrame:
    """Fishing vessels, GFW-flagged intentional disabling, gap shorter than max_hours."""
    needed = {"v_type", "g_intentional_disabling", "g_duration_hours"}
    if not needed.issubset(flat.columns):
        return flat.iloc[0:0]
    mask = (
        (flat["v_type"] == "fishing")
        & (flat["g_intentional_disabling"] == True)  # noqa: E712 (pandas needs ==)
        & (flat["g_duration_hours"] < max_hours)
    )
    return flat[mask].copy()


def repeat_gap_vessel_ids(short: pd.DataFrame) -> list[str]:
    """IDs of vessels with more than one short gap."""
    if "v_id" not in short.columns:
        return []
    counts = short["v_id"].value_counts()
    return counts[counts > 1].index.tolist()


def per_vessel_counts(events_df: pd.DataFrame) -> pd.DataFrame:
    """One row per fishing vessel: how many fishing-carrier encounters it had."""
    v = pd.json_normalize(events_df["vessel"].tolist()).add_prefix("v_")
    x = pd.json_normalize(events_df["encounter"].tolist()).add_prefix("e_")
    flat = pd.concat([events_df[["id"]].reset_index(drop=True), v, x], axis=1)
    flat = flat[(flat["v_type"] == "fishing") & (flat["e_type"].astype(str).str.lower() == "fishing-carrier")]
    return (
        flat.groupby("v_id")
        .agg(n_encounters=("id", "nunique"), v_name=("v_name", "first"), v_flag=("v_flag", "first"))
        .reset_index()
        .sort_values("n_encounters", ascending=False)
        .reset_index(drop=True)
    )


def rank_of(count: int, counts: pd.Series) -> dict:
    """How one vessel's encounter count compares with everyone's."""
    n = len(counts)
    return {
        "count": int(count),
        "vessels_with_fewer": int((counts < count).sum()),
        "vessels_with_same_or_more": int((counts >= count).sum()),
        "share_with_same_or_more_pct": round(float(100 * (counts >= count).mean()), 1) if n else 0.0,
    }
