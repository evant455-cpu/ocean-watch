# ocean-watch

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/evant455-cpu/ocean-watch/blob/main/notebooks/colab_quickstart.ipynb) ![tests](https://github.com/evant455-cpu/ocean-watch/actions/workflows/tests.yml/badge.svg)


Open-data ocean monitoring built on [Global Fishing Watch](https://globalfishingwatch.org/our-apis/) (GFW).
It pulls fishing activity, radar ship detections, and tracker-off ("gap") events for a chosen sea area,
then turns them into maps and short summaries. Personal, non-commercial, learning-first.

**What it answers so far**
- Where is fishing happening, and how much? (AIS apparent fishing effort)
- How many ships does radar see that no tracker identifies? (SAR detections with no AIS match)
- Which fishing vessels went quiet for a short time? (AIS gap events)
- Are the vessels of interest unusual in how often they meet cargo carriers at sea? (encounter baseline)

Everything it produces is a **lead, not evidence**. See [docs/methodology.md](docs/methodology.md).

## Quick start

### On a phone or any browser (Google Colab)
Open `notebooks/colab_quickstart.ipynb` in Colab and run the cells in order. Save your GFW token in
Colab **Secrets** (key icon) under the name `GFW_TOKEN`, with notebook access turned on.

### On a computer
```bash
git clone https://github.com/evant455-cpu/ocean-watch.git
cd ocean-watch
pip install -e .            # needs Python 3.11+
cp .env.example .env        # then paste your token into .env (git-ignored)

oceanwatch run              # fishing effort + radar + gaps -> output/
oceanwatch baseline         # rank vessels of interest on carrier encounters -> output/
```
Try another area or period:
```bash
oceanwatch run --region-id 8371 --start 2023-01-01 --end 2023-06-01
```
Get a token (free, non-commercial): https://globalfishingwatch.org/our-apis/tokens

## Layout
```
src/oceanwatch/
  config.py      run settings (region, dates, thresholds) and token lookup
  fetch.py       every GFW API call (the only file that touches the network)
  analysis.py    pure pandas logic, easy to test
  plots.py       maps and charts (always credit GFW)
  workflows.py   end-to-end runs that write CSVs, PNGs, and a summary
  cli.py         the `oceanwatch` command
tests/           pytest, using a fake client (no network, no token needed)
notebooks/       Colab quick start
docs/            methodology, glossary, roadmap, dated findings
CLAUDE.md        context file so a new Claude session can pick up where we left off
```

## Adding a new analysis
1. Add the API call to `fetch.py` (returns a DataFrame).
2. Add the logic to `analysis.py` (pure function, no network).
3. Add a chart to `plots.py` if needed.
4. Wire it into a function in `workflows.py` and a subcommand in `cli.py`.
5. Add tests using the fake client in `tests/conftest.py`, then `pytest`.
6. Write up results in `docs/findings/` (no vessel names) and update `docs/ROADMAP.md`.

## Ground rules
- **Never commit the token.** It lives in Colab Secrets, an environment variable, or a git-ignored `.env`.
- **Never commit vessel names or generated output.** `output/` is git-ignored on purpose.
- **Credit Global Fishing Watch** in anything published. GFW data is for non-commercial use only.
- **Leads, not evidence.** Gaps, unmatched radar detections, and encounters all have innocent explanations.

## License
None chosen yet. Add one before inviting outside contributions.
