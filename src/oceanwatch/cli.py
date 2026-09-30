"""Command line: `oceanwatch run` and `oceanwatch baseline` (or `python -m oceanwatch ...`)."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from oceanwatch import __version__
from oceanwatch.config import RunConfig
from oceanwatch.workflows import run_baseline, run_pipeline


def _add_common(p: argparse.ArgumentParser) -> None:
    d = RunConfig()
    p.add_argument("--region-dataset", default=d.region_dataset, help="GFW region dataset (default: EEZ areas)")
    p.add_argument("--region-id", default=d.region_id, help="GFW region id (default: 5690, Russian EEZ)")
    p.add_argument("--start", default=d.start_date, help="start date YYYY-MM-DD")
    p.add_argument("--end", default=d.end_date, help="end date YYYY-MM-DD")
    p.add_argument("--out", default=str(d.out_dir), help="output folder (default: output)")


def _config(a: argparse.Namespace) -> RunConfig:
    return RunConfig(region_dataset=a.region_dataset, region_id=str(a.region_id),
                     start_date=a.start, end_date=a.end, out_dir=Path(a.out))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="oceanwatch", description="Ocean monitoring with Global Fishing Watch data.")
    parser.add_argument("--version", action="version", version=f"oceanwatch {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="fishing effort + radar detections + AIS gaps, with maps and a summary")
    _add_common(run)
    run.add_argument("--max-gap-hours", type=float, default=RunConfig().max_gap_hours)

    base = sub.add_parser("baseline", help="rank vessels of interest on fishing-carrier encounters")
    _add_common(base)
    base.add_argument("--vessel-ids", nargs="+", help="GFW vessel ids (default: repeat-gap vessels from the last run)")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    cfg = _config(args)
    if args.command == "run":
        cfg = RunConfig(**{**cfg.__dict__, "max_gap_hours": args.max_gap_hours})
        asyncio.run(run_pipeline(cfg))
    elif args.command == "baseline":
        asyncio.run(run_baseline(cfg, vessel_ids=args.vessel_ids))


if __name__ == "__main__":
    main()
