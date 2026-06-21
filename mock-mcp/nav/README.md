# `nav` — Fund NAV pack (mock, read-only, source of truth)

Stands in for the `nav` MCP (`NAV_MCP_URL`). The authoritative NAV figures that
draft LP statements are audited against.

- **Used by:** `statement-auditor`
- **Default HTTP port:** `8004`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8004`

## Tools

| Tool | Purpose |
|---|---|
| `list_funds()` | Discover funds / as-of dates |
| `get_nav_build(fund, as_of)` | Fund-level NAV build (assets − liabilities = NAV) |
| `get_lp_capital_accounts(fund, as_of, lp_id?)` | Per-LP capital accounts + column totals |

## Data

Fund **Aurora Growth Fund**, as-of **2026-03-31**. NAV **112,437,500** ties to the
sum of LP ending balances. Each LP row foots: beginning + contributions −
distributions + net_gain_loss − mgmt_fee = ending.

## Testing note

This MCP serves the **correct** figures. The *draft LP statement* the auditor reads
(in `docs/outputs/statement-auditor/samples/.../lp_statement.md`) has **planted errors**
to be caught by comparing against this pack, e.g.:

- LP-001 mgmt fee 200,000 (draft) vs **250,000** (NAV pack)
- LP-002 ending 31,321,500 (draft) vs **31,312,500** (NAV pack)
- LP-003 contributions 2,500,000 (draft) vs **2,000,000** (NAV pack)
- Draft TOTAL ending 112,996,500 vs NAV **112,437,500**

Source: `docs/outputs/statement-auditor/samples/statement-auditor/nav_pack.md`.
