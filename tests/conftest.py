"""Shared fake data shaped like the real GFW output, plus a fake client (no network)."""

import pandas as pd
import pytest


class FakeResult:
    def __init__(self, df):
        self._df = df

    def df(self):
        return self._df


def effort_df():
    return pd.DataFrame({
        "date": ["2022-01", "2022-02", "2022-03"] * 4,
        "flag": ["RUS"] * 12,
        "hours": [1.0, 5.0, 20.0, 3.0, 8.0, 40.0, 2.0, 6.0, 12.0, 77.0, 9.0, 4.0],
        "lat": [50.0, 51.0, 52.0, 53.0] * 3,
        "lon": [140.0, 145.0, 150.0, 155.0] * 3,
    })


def sar_df():
    return pd.DataFrame({
        "flag": ["PAN", "RUS", "", None],
        "detections": [1, 1, 1, 3],
        "lat": [44.5, 50.2, 46.2, 47.0],
        "lon": [37.6, 156.5, 149.2, 150.0],
    })


def gaps_df():
    def gap(hours, disabling=True):
        return {"intentional_disabling": disabling, "duration_hours": str(hours),
                "off_position": {"lat": 50.0, "lon": 150.0}}

    def vessel(vid, name, vtype="fishing"):
        return {"id": vid, "name": name, "type": vtype, "flag": "RUS"}

    return pd.DataFrame({
        "start": pd.to_datetime(["2022-01-01", "2022-01-05", "2022-02-01", "2022-02-10", "2022-03-01"], utc=True),
        "end": pd.to_datetime(["2022-01-02", "2022-01-06", "2022-02-02", "2022-02-11", "2022-03-02"], utc=True),
        "vessel": [vessel("A", "ALPHA"), vessel("A", "ALPHA"), vessel("B", "BRAVO"),
                   vessel("C", "CARGO", "cargo"), vessel("D", "DELTA")],
        "gap": [gap(20), gap(30), gap(500), gap(10), gap(15, disabling=False)],
    })


def encounter_rows(n_vessels=30, target_counts=None):
    """Encounter events: vessel v0..v{n-1} with 1-3 encounters, plus vessels 'A','B' with target counts."""
    rows, i = [], 0

    def ev(vid, name, etype="fishing-carrier", vtype="fishing"):
        nonlocal i
        i += 1
        return {"id": f"e{i}", "vessel": {"id": vid, "name": name, "type": vtype, "flag": "RUS"},
                "encounter": {"type": etype}}

    for v in range(n_vessels):
        for _ in range(1 + v % 3):
            rows.append(ev(f"v{v}", f"V{v}"))
    for vid, n in (target_counts or {"A": 4, "B": 2}).items():
        for _ in range(n):
            rows.append(ev(vid, vid))
    rows.append(ev("car1", "CARRIER", etype="carrier-fishing", vtype="carrier"))  # must be excluded
    return pd.DataFrame(rows)


class FakeFourWings:
    async def create_fishing_effort_report(self, **kw):
        return FakeResult(effort_df())

    async def create_sar_presence_report(self, **kw):
        return FakeResult(sar_df())


class FakeEvents:
    def __init__(self, encounters):
        self.encounters = encounters
        self.calls = []

    async def get_all_events(self, **kw):
        self.calls.append(kw)
        if kw["datasets"] == ["public-global-gaps-events:latest"]:
            return FakeResult(gaps_df())
        o, l = kw.get("offset", 0), kw.get("limit", 100)
        return FakeResult(self.encounters.iloc[o:o + l].reset_index(drop=True))


class FakeClient:
    def __init__(self, encounters=None):
        self.fourwings = FakeFourWings()
        self.events = FakeEvents(encounters if encounters is not None else encounter_rows())


@pytest.fixture
def fake_client():
    return FakeClient()
