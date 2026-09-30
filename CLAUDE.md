# CLAUDE.md: context for future Claude sessions

## Project
`ocean-watch` is a personal, non-commercial learning project using Global Fishing Watch (GFW) open data to
study fishing activity and ship-tracking gaps. The owner is a self-taught developer who cares about ocean
life and wants real conservation value from public data. Read `README.md`, then `docs/ROADMAP.md`
(what is done and what is next) and `docs/methodology.md` (how to read the results).

## Working style the owner prefers
- Keep explanations brief and to the point.
- Explain every new term or abbreviation the first time it appears (also add it to `docs/glossary.md`).
- Diagnose before acting: check the current state of files and environment before changing things.
- The owner is often on a phone. Prefer runnable files, the CLI, or the Colab notebook over pasting long
  multi-line code (pasted indentation breaks). If code must be pasted, avoid indented lines.

## Hard rules
- Never write the API token (or any secret) into code, docs, commits, or chat. Token sources, in order:
  env var `GFW_API_ACCESS_TOKEN`, a git-ignored `.env`, a hidden prompt. In Colab it is the secret `GFW_TOKEN`.
- Never commit vessel names, vessel IDs, or anything from `output/`. Refer to vessels as A, B, C in docs.
- Credit Global Fishing Watch on every chart and in every write-up. Non-commercial use only.
- Findings are leads, not evidence. Do not describe any vessel as illegal or accuse anyone.
- Only call API parameters that were verified against the GFW docs or the installed package signature
  (`inspect.signature`). Say plainly when something was not tested against the live API.

## Verified facts about the GFW client (gfw-api-python-client 1.4.x)
- Async API: `await client.fourwings.create_fishing_effort_report(...)`, `create_sar_presence_report(...)`,
  `await client.events.get_all_events(datasets=[...], start_date, end_date, region, limit, offset, vessels, encounter_types)`.
- Results have `.df()` (pandas) and `.data()` (pydantic). Event rows have nested `vessel`, `gap`, `encounter`,
  `position` dicts, flattened with `pd.json_normalize`.
- Datasets used: `public-global-gaps-events:latest`, `public-global-encounters-events:latest`.
- Encounters are detected from AIS positions, so meetings during a tracker-off gap can never appear.
- Python 3.11+ is required; the package pulls in geopandas, which does not install on Android (Pydroid).

## Conventions
- All network calls live in `fetch.py`; `analysis.py` stays pure so it can be tested with fake data.
- New behaviour needs a test in `tests/` using the fake client. Run `pytest` before committing.
- Commit small and often; write findings to `docs/findings/YYYY-MM-<slug>.md`.

## Where progress is tracked
A Notion page ("Marine Conservation & Research") holds the running log and glossary. `docs/ROADMAP.md`
is the source of truth for next steps in this repo.
