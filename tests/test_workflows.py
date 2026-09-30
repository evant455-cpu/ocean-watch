import asyncio

import pandas as pd
import pytest

from conftest import FakeClient, encounter_rows
from oceanwatch import cli, fetch
from oceanwatch.config import RunConfig, get_token
from oceanwatch.workflows import load_repeat_gap_ids, run_baseline, run_pipeline


def test_paging_collects_every_row_and_stops(fake_client):
    cfg = RunConfig(page_size=10)
    df = asyncio.run(fetch.encounter_events(fake_client, cfg))
    assert len(df) == len(fake_client.events.encounters)
    assert df["id"].is_unique


def test_paging_with_vessel_ids_uses_vessels_not_region(fake_client):
    asyncio.run(fetch.encounter_events(fake_client, RunConfig(), vessel_ids=["A"]))
    call = fake_client.events.calls[0]
    assert call["vessels"] == ["A"] and "region" not in call


def test_paging_stops_when_pages_repeat():
    same = encounter_rows(5)
    client = FakeClient(same)
    client.events.encounters = pd.concat([same, same], ignore_index=True)  # ids repeat on page 2
    df = asyncio.run(fetch.encounter_events(client, RunConfig(page_size=len(same))))
    assert df["id"].is_unique


def test_run_pipeline_end_to_end(tmp_path, fake_client):
    cfg = RunConfig(out_dir=tmp_path)
    out = asyncio.run(run_pipeline(cfg, client=fake_client))
    assert out["sar_unidentified_pct"] == 66.7 and out["short_gaps"] == 2
    for name in ("fishing_effort.csv", "sar_detections.csv", "short_gaps_fishing_vessels.csv",
                 "map_fishing_effort.png", "map_unidentified_and_gaps.png", "summary.txt"):
        assert (tmp_path / name).exists(), name
    assert load_repeat_gap_ids(cfg) == ["A"]


def test_run_baseline_end_to_end(tmp_path, fake_client):
    cfg = RunConfig(out_dir=tmp_path)
    asyncio.run(run_pipeline(cfg, client=fake_client))       # creates the gaps CSV it reads
    out = asyncio.run(run_baseline(cfg, client=fake_client))
    assert out["ranks"]["A"]["count"] == 4
    for name in ("encounters_per_fishing_vessel.csv", "baseline_histogram.png", "baseline_summary.txt"):
        assert (tmp_path / name).exists(), name
    # vessel names must never appear in the printed/saved summary
    assert "ALPHA" not in (tmp_path / "baseline_summary.txt").read_text()


def test_baseline_without_prior_run_gives_clear_error(tmp_path, fake_client):
    with pytest.raises(FileNotFoundError, match="oceanwatch run"):
        asyncio.run(run_baseline(RunConfig(out_dir=tmp_path), client=fake_client))


def test_token_order_env_then_file(monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text('GFW_API_ACCESS_TOKEN="from-file"\n')
    monkeypatch.delenv("GFW_API_ACCESS_TOKEN", raising=False)
    assert get_token(env_file) == "from-file"
    monkeypatch.setenv("GFW_API_ACCESS_TOKEN", "from-env")
    assert get_token(env_file) == "from-env"


def test_cli_parses_and_applies_options():
    args = cli.build_parser().parse_args(["run", "--region-id", "8371", "--start", "2023-01-01", "--max-gap-hours", "48"])
    cfg = cli._config(args)
    assert cfg.region == {"dataset": "public-eez-areas", "id": "8371"}
    assert cfg.start_date == "2023-01-01" and args.max_gap_hours == 48
