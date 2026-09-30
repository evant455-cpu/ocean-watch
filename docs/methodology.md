# Methodology and caveats

## Data sources (all from Global Fishing Watch, non-commercial use, credit GFW)
| Question | GFW API | Function |
|---|---|---|
| Where and how much fishing? | 4Wings, AIS apparent fishing effort | `fetch.fishing_effort` |
| What does radar see? | 4Wings, SAR vessel detections | `fetch.sar_detections` |
| Who went dark? | Events, gap events | `fetch.gap_events` |
| Who met a carrier at sea? | Events, encounter events | `fetch.encounter_events` |

## How each result is built
- **Apparent fishing effort**: hours a vessel's movement pattern looks like fishing. An estimate, not proof.
  Only ships broadcasting AIS appear.
- **Unidentified share**: SAR detections with a blank flag, divided by all SAR detections. Radar sees every
  kind of ship (cargo, tankers, ferries, naval), so a blank flag is not "illegal fishing".
- **Short gap**: a fishing vessel, GFW flagged `intentional_disabling`, gap under `max_gap_hours` (default 72).
  Very long gaps (months or years) are usually retired transmitters or data artifacts, so they are excluded.
- **Encounter baseline**: count fishing-carrier encounters per fishing vessel across the whole region, then
  see where vessels of interest rank.

## Known limits (read before drawing conclusions)
1. **AIS-only detection of encounters.** A meeting while a tracker was off cannot be seen. The absence of
   encounters inside a gap proves nothing.
2. **Baseline bias.** The baseline only includes vessels with at least one encounter, so it runs high. If a
   vessel does not stand out here, it would not stand out against the whole fleet either. The reverse is not
   safe: ranking high does not prove anything.
3. **Gaps have innocent causes**: equipment faults, weak satellite reception, ships in port or at anchor.
4. **Authorization status** ("not matching relevant public authorization") means no match in the public lists
   GFW has. It does not mean a vessel lacks a licence. The same vessel can change status across dates.
5. **Region filter behaviour.** Event queries with a region return events inside it, but gap events can start
   or end far outside; check positions.
6. **Small samples.** Three vessels over four months cannot support statistical claims.
7. **Antimeridian.** Longitude wraps at 180, so one fleet can appear at both -180 and +180 on a map.

## Ethics
Findings are leads for a researcher to check. Do not publish vessel names or imply wrongdoing. Keep results
private unless a domain expert has reviewed them.
