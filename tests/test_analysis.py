import pandas as pd

from conftest import encounter_rows, gaps_df, sar_df
from oceanwatch import analysis


def test_unidentified_share_counts_blank_and_missing_flags():
    dark, dark_total, all_total, pct = analysis.unidentified_share(sar_df())
    assert (dark_total, all_total, pct) == (4, 6, 66.7)
    assert len(dark) == 2


def test_unidentified_share_handles_empty():
    empty = pd.DataFrame({"flag": [], "detections": []})
    assert analysis.unidentified_share(empty)[1:] == (0, 0, 0.0)


def test_flatten_and_short_gaps_filter():
    flat = analysis.flatten_gaps(gaps_df())
    assert {"v_id", "v_name", "v_type", "g_duration_hours", "g_off_position.lon"} <= set(flat.columns)
    short = analysis.short_fishing_gaps(flat, 72)
    # kept: A (20 h), A (30 h). dropped: B (500 h too long), cargo, D (not flagged intentional)
    assert sorted(short["v_id"]) == ["A", "A"]


def test_short_gaps_on_missing_columns_returns_empty():
    assert len(analysis.short_fishing_gaps(pd.DataFrame({"start": [1]}), 72)) == 0


def test_repeat_gap_vessel_ids():
    short = analysis.short_fishing_gaps(analysis.flatten_gaps(gaps_df()), 72)
    assert analysis.repeat_gap_vessel_ids(short) == ["A"]


def test_per_vessel_counts_excludes_non_fishing_carrier_rows():
    pv = analysis.per_vessel_counts(encounter_rows())
    assert "car1" not in set(pv["v_id"])
    lookup = dict(zip(pv["v_id"], pv["n_encounters"]))
    assert lookup["A"] == 4 and lookup["B"] == 2


def test_rank_of():
    counts = pd.Series([1, 1, 2, 3, 4])
    r = analysis.rank_of(3, counts)
    assert r["vessels_with_fewer"] == 3
    assert r["vessels_with_same_or_more"] == 2
    assert r["share_with_same_or_more_pct"] == 40.0
