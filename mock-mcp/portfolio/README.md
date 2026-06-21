# `portfolio` — PE portfolio data source (mock, read-only)

Stands in for the `portfolio` MCP (`PORTFOLIO_MCP_URL`).

- **Used by:** `valuation-reviewer`
- **Default HTTP port:** `8003`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8003`

## Tools

| Tool | Purpose |
|---|---|
| `list_funds()` | Discover funds / as-of dates |
| `get_positions(fund, as_of)` | GP-reported marks per portfolio company (the review target) |
| `get_fund_nav_build(fund, as_of)` | Fund-level NAV build |
| `get_capital_flows(fund)` | Contributions / distributions / ending NAV (IRR & MOIC) |
| `get_fund_terms(fund)` | Commitments, hurdle 8%, catch-up 100%, carry 20%, accrued pref |
| `get_valuation_policy(fund)` | Review rules P1–P4 |

## Data

Fund **Aurora Growth Fund III, L.P.**, as-of **2026-03-31**. NAV as-reported
350,000,000; committed 500M / contributed 300M / distributed 40M.

## Planted for testing (policy breaches the reviewer must catch)

| Company | GP mark | Issue | Rule |
|---|---|---|---|
| Nova Biotech | +62% to 65M, `other` (management estimate) | No method, no round, no trigger | **P2 breach** |
| Zephyr Retail | flat at cost, last updated **2025-03** | Stale > 2 quarters | **P1 breach** |
| Helios Software | +33% via `market_multiple` | Has comps table + 2025-09 round support | OK |
| Orion Logistics | flat, `recent_round` | Carried at last round | OK |
| Titan Manufacturing | flat, `dcf`, below cost | Impairment reflected | OK |

Source: `docs/outputs/valuation-reviewer/samples/gp_valuation_package_2026-Q1.md`,
`fund_terms_and_positions_2026-Q1.md`.
