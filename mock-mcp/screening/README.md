# `screening` — Sanctions / PEP screening (mock, read-only)

Stands in for the `screening` MCP (`SCREENING_MCP_URL`).

- **Used by:** `kyc-screener`
- **Default HTTP port:** `8006`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8006`

## Tools

| Tool | Purpose |
|---|---|
| `screen_name(name, dob?, country?)` | Identifier-aware match → classification + action |
| `get_sanctions_list()` | Full sanctions watchlist |
| `get_pep_list()` | Full PEP watchlist |

`screen_name` returns one entry per candidate, classified as `confirmed_sanctions_match`
/ `potential_sanctions_match` / `likely_false_positive` / `pep_match`, plus an overall
verdict (`HIT_SANCTIONS` / `HIT_PEP` / `REVIEW` / `CLEAR`). It only **confirms** a hit
when name **and** DOB **and** country align — a name match with a different DOB/country
is a likely false positive to be cleared, not auto-rejected.

## Planted for testing (drives the onboarding cases in the kyc-screener sample)

| Applicant (from sample) | Screen input | Expected |
|---|---|---|
| Ivan Petrov | `Ivan Petrov, 1970-03-15, Russia` | **confirmed** (S-1) → R4 reject/escalate |
| Maria Garcia | `Maria Garcia, 1988-11-02, Spain` | **likely_false_positive** (S-2 is 1955/Colombia) → clear |
| Adewale Okonkwo (UBO) | `Adewale Okonkwo, , Nigeria` | **pep_match** (P-1) → R5 EDD |
| Robert Quiet / Sarah Brook | their names | **CLEAR** |

Sources: `docs/outputs/kyc-screener/samples/sanctions_pep_watchlist.md`,
`onboarding_applications_2026-06.md`.
