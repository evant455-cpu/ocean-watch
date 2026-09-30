# Roadmap

## Done
- [x] GFW account and API token (kept in Colab Secrets, never in the repo)
- [x] AIS apparent fishing effort report and map
- [x] SAR detections and unidentified share (first baseline: 25.5% for the Russian EEZ, Jan-Apr 2022)
- [x] AIS-gap events, short-gap shortlist for fishing vessels
- [x] Encounter check for vessels with repeat gaps
- [x] Encounter baseline script (written and tested on fake data; live run pending, see below)
- [x] Package, CLI, tests, and Colab notebook

## Next (roughly in priority order)
- [ ] Run `oceanwatch baseline` against the live API and record the result in `docs/findings/`
- [ ] Marine Protected Area workflow: look up an MPA id with the GFW References API, then compare fishing
      inside versus along its boundary (needs a `fetch.regions` function and a boundary-distance step)
- [ ] Run `oceanwatch run` on other regions and compare unidentified shares against the 25.5% baseline
- [ ] Look up what GFW's public-authorization status covers, and whether it explains the March result
- [ ] Widen the date range; add monthly and per-flag summaries
- [ ] Loitering and port-visit events (Events API)
- [ ] Optional: vessel insights (Insights API) for risk context on individual leads

## Later ideas
- [x] Continuous integration (GitHub Actions runs `pytest` on every push)
- [ ] A small dashboard or static report page for results
- [ ] Floating-plastic detection from Sentinel-2 imagery (open problem, different data source)
- [ ] Choose a license before accepting outside contributions
