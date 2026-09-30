"""Maps and charts. They draw to PNG files (no window needed) and always carry the GFW credit."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from oceanwatch.config import CREDIT, RunConfig


def effort_map(effort_df: pd.DataFrame, cfg: RunConfig, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(
        effort_df["lon"], effort_df["lat"], c=effort_df["hours"], s=15, cmap="viridis",
        vmax=effort_df["hours"].quantile(0.95),
    )
    fig.colorbar(sc, label="Apparent fishing hours")
    ax.set(xlabel="Longitude", ylabel="Latitude",
           title=f"Apparent fishing effort, {cfg.start_date} to {cfg.end_date}")
    fig.text(0.01, 0.01, CREDIT, fontsize=7)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def unidentified_and_gaps_map(effort_df: pd.DataFrame, dark: pd.DataFrame, short: pd.DataFrame,
                              cfg: RunConfig, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(effort_df["lon"], effort_df["lat"], c="lightblue", s=10, label="AIS fishing")
    ax.scatter(dark["lon"], dark["lat"], c="red", s=12, marker="x", label="Radar, no AIS match")
    lon_col, lat_col = "g_off_position.lon", "g_off_position.lat"
    if lon_col in short.columns and len(short):
        ax.scatter(short[lon_col], short[lat_col], c="black", s=40, marker="^",
                   label="Fishing vessel tracker went silent")
    ax.legend()
    ax.set(xlabel="Longitude", ylabel="Latitude", title="Fishing effort vs unidentified radar detections")
    fig.text(0.01, 0.01, CREDIT, fontsize=7)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def baseline_histogram(counts: pd.Series, labels: dict[str, int], cfg: RunConfig, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(counts, bins=range(1, int(counts.max()) + 2), color="lightblue", edgecolor="white", align="left")
    for label, c in labels.items():
        ax.axvline(c, color="red", linestyle="--", alpha=0.7)
        ax.text(c, ax.get_ylim()[1] * 0.95, label, color="red", ha="center", va="top")
    ax.set(xlabel="Fishing-carrier encounters per vessel", ylabel="Number of fishing vessels",
           title=f"Encounter baseline, {cfg.start_date} to {cfg.end_date}")
    fig.text(0.01, 0.01, CREDIT, fontsize=7)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
