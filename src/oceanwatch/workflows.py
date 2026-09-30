"""End-to-end workflows. Each one takes a RunConfig, writes CSVs / PNGs / a text summary into
cfg.out_dir, and returns its headline numbers as a dict. Pass a client to reuse one (or a fake in
tests); otherwise one is built from the token."""

from __future__ import annotations

import pandas as pd

from oceanwatch import analysis, fetch, plots
from oceanwatch.config import RunConfig, get_token

SHORT_GAPS_CSV = "short_gaps_fishing_vessels.csv"

REMINDER = [
    "Reminder: these are leads, not evidence. Gaps and unmatched radar detections have many innocent",
    "causes (equipment faults, patchy satellite coverage, non-fishing ships). Credit Global Fishing Watch.",
]


def _client(client):
    if client is not None:
        return client
    import gfwapiclient as gfw

    return gfw.Client(access_token=get_token())


async def run_pipeline(cfg: RunConfig, client=None) -> dict:
    """Fishing effort + SAR detections + AIS gaps, with two maps and a summary."""
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    client = _client(client)

    print("1/3 Fishing effort ...")
    effort_df = await fetch.fishing_effort(client, cfg)
    effort_df.to_csv(cfg.out_dir / "fishing_effort.csv", index=False)

    print("2/3 SAR (radar) detections ...")
    sar_df = await fetch.sar_detections(client, cfg)
    sar_df.to_csv(cfg.out_dir / "sar_detections.csv", index=False)
    dark, dark_total, all_total, pct = analysis.unidentified_share(sar_df)

    print("3/3 AIS gap events ...")
    flat = analysis.flatten_gaps(await fetch.gap_events(client, cfg))
    short = analysis.short_fishing_gaps(flat, cfg.max_gap_hours)
    short.to_csv(cfg.out_dir / SHORT_GAPS_CSV, index=False)

    plots.effort_map(effort_df, cfg, cfg.out_dir / "map_fishing_effort.png")
    plots.unidentified_and_gaps_map(effort_df, dark, short, cfg, cfg.out_dir / "map_unidentified_and_gaps.png")

    repeat = short["v_name"].value_counts() if "v_name" in short.columns else pd.Series(dtype=int)
    lines = [
        f"Region: {cfg.region}   Dates: {cfg.start_date} to {cfg.end_date}",
        f"Fishing effort grid rows: {len(effort_df)}   total apparent hours: {effort_df['hours'].sum():.0f}",
        f"SAR detections: {all_total}   unidentified (no AIS match): {dark_total} ({pct}%)",
        f"Gap events pulled: {len(flat)}   short (<{cfg.max_gap_hours:g} h) gaps by fishing vessels: {len(short)}",
        "",
        "Vessels with more than one short gap:",
        repeat[repeat > 1].to_string() if (repeat > 1).any() else "  none",
        "",
        *REMINDER,
    ]
    (cfg.out_dir / "summary.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nFiles saved in: {cfg.out_dir}")
    return {"effort_rows": len(effort_df), "sar_total": all_total, "sar_unidentified": dark_total,
            "sar_unidentified_pct": pct, "gap_events": len(flat), "short_gaps": len(short)}


def load_repeat_gap_ids(cfg: RunConfig) -> list[str]:
    path = cfg.out_dir / SHORT_GAPS_CSV
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `oceanwatch run` first, or pass --vessel-ids explicitly."
        )
    return analysis.repeat_gap_vessel_ids(pd.read_csv(path))


async def run_baseline(cfg: RunConfig, client=None, vessel_ids: list[str] | None = None) -> dict:
    """Where do the repeat-gap vessels rank on fishing-carrier encounters among all fishing vessels?"""
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    client = _client(client)
    targets = vessel_ids or load_repeat_gap_ids(cfg)

    print("Pulling all fishing-carrier encounters in the region ...")
    events = await fetch.encounter_events(client, cfg)
    if events.empty:
        print("No encounters returned; nothing to compare.")
        return {"encounters": 0}

    per_vessel = analysis.per_vessel_counts(events)
    per_vessel.to_csv(cfg.out_dir / "encounters_per_fishing_vessel.csv", index=False)
    counts = per_vessel["n_encounters"]
    lookup = dict(zip(per_vessel["v_id"], per_vessel["n_encounters"]))

    lines = [
        f"Region: {cfg.region}   Dates: {cfg.start_date} to {cfg.end_date}",
        f"Fishing-carrier encounters pulled: {len(events)}",
        f"Fishing vessels with at least one such encounter: {len(per_vessel)}",
        f"Encounters per vessel: median {counts.median():.0f}, mean {counts.mean():.1f}, "
        f"75th pct {counts.quantile(0.75):.0f}, 90th pct {counts.quantile(0.90):.0f}, max {counts.max()}",
        "",
        "Vessels of interest (labelled A, B, C...; names are in the CSV, not printed here):",
    ]
    labels, ranks = {}, {}
    for i, vid in enumerate(targets):
        label = "ABCDEFGH"[i] if i < 8 else str(i)
        c = lookup.get(vid, 0)
        labels[label] = c
        ranks[label] = analysis.rank_of(c, counts)
        r = ranks[label]
        lines.append(f"  {label}: {c} encounters; {r['vessels_with_same_or_more']} of {len(counts)} vessels "
                     f"({r['share_with_same_or_more_pct']}%) had the same or more")
    lines += [
        "",
        "How to read this: the baseline only includes vessels with at least one encounter, so it is",
        "biased HIGH (vessels with zero encounters are missing). If the vessels of interest do not stand",
        "out here, they would not stand out against the whole fleet either. Encounters are detected from",
        "AIS, so this says nothing about meetings that happened while a tracker was off.",
        "Leads, not evidence. Credit Global Fishing Watch.",
    ]
    (cfg.out_dir / "baseline_summary.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))

    plots.baseline_histogram(counts, labels, cfg, cfg.out_dir / "baseline_histogram.png")
    print(f"\nFiles saved in: {cfg.out_dir}")
    return {"encounters": len(events), "vessels": len(per_vessel), "ranks": ranks}
