# `internal-gl` — General Ledger (mock, read-only)

Stands in for the `internal-gl` MCP (`GL_MCP_URL`). **Read-only** — no posting tools.

- **Used by:** `month-end-closer` (trial balance + journal drill), `gl-reconciler` (GL-side positions)
- **Default HTTP port:** `8001`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8001`

## Tools

| Tool | Purpose |
|---|---|
| `list_entities()` | Discover available entities/funds and periods |
| `get_trial_balance(entity, period)` | Trial balance with prior/current YTD, movement %, and Dr=Cr check |
| `get_journal_entries(entity, account?, start_date?, end_date?, source?)` | Drill JE lines to explain a flux |
| `get_account_balance(entity, account, period)` | One account's prior/current balance |
| `get_gl_positions(fund, as_of)` | Position-level GL balances (recon's GL side) |

## Data

| File | Rows | Notes |
|---|---|---|
| `trial_balance.csv` | 18 accts | Entity **Aurora Capital Management LLC**, period **2026-04**, pre-close. Dr=Cr=21,380,000 ✓ |
| `journal_entries.csv` | 11 | April activity for the big movers (prof. fees, travel, IT, rent, payroll, accrual reversal) |
| `gl_positions.csv` | 9 | Fund **Aurora Growth Fund III**, as-of **2026-04-30**, total 84,500,000 |

## Planted for testing

The GL positions are deliberately **out of step with the subledger** so `gl-reconciler`
has real breaks to find (compare with the [`subledger/`](../subledger/) mock):

- `EQ-VRT` qty 50,000 (GL) vs 52,500 (custody) — quantity break
- `FI-XYZ` 20,000,000 (GL) vs 19,000,000 (custody) — face break
- `CA-USD` 3,000,000 (GL) vs 2,400,000 (custody) — cash break
- `EQ-SPY` classed `Equity` in GL vs `Funds/ETF` in custody — reclass (not a real break)

Sources: reverse-engineered from `docs/outputs/month-end-closer/samples/trial_balance_2026-04.md`,
`docs/outputs/gl-conciler/samples/gl_balances_2026-04-30.md`.
