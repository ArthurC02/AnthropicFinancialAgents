# `subledger` — Custody / position sub-ledger (mock, read-only)

Stands in for the `subledger` MCP (`SUBLEDGER_MCP_URL`). The custody side of the
reconciliation plus the reference data to classify each break.

- **Used by:** `gl-reconciler`
- **Default HTTP port:** `8002`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8002`

## Tools

| Tool | Purpose |
|---|---|
| `get_subledger_holdings(fund, as_of)` | Custody holdings (settlement-date) — the recon's custody side |
| `get_pending_settlements(fund, as_of)` | Traded-not-settled list → explains *timing* breaks |
| `get_fx_rates(as_of, pair?)` | GL vs custody FX rates → explains *rounding* breaks |
| `get_tolerance_policy()` | Break thresholds (abs 0.01 USD, qty 0, FX rounding 0.05%) |

## Data

| File | Notes |
|---|---|
| `subledger_holdings.csv` | Fund **Aurora Growth Fund III**, as-of **2026-04-30**, total 82,650,300 |
| `pending_settlements.csv` | One trade `TRD-9001` (GB123 buy, settles 2026-05-02) |
| `fx_rates.csv` | EUR/USD GL 1.08000 vs custody 1.08004 |

## Planted for testing (vs the [`internal-gl`](../internal-gl/) GL side)

| Break | GL | Custody | True cause |
|---|---|---|---|
| `EQ-VRT` qty | 50,000 | 52,500 | **Real break** — not on the pending blotter |
| `FI-XYZ` face | 20,000,000 | 19,000,000 | **Real break** — system lag / unrecorded sale |
| `CA-USD` cash | 3,000,000 | 2,400,000 | **Real break** — investigate |
| `FI-GB123` face | 15,500,000 | 15,000,000 | **Timing** — TRD-9001 settles 2026-05-02 |
| `FI-BUND` MV | 9,000,000 | 9,000,300 | **FX rounding** — within 0.05% (EUR/USD precision) |
| `EQ-SPY` class | Equity | Funds/ETF | **Reclass** — same qty & MV, different classification |

Source: `docs/outputs/gl-conciler/samples/subledger_holdings_2026-04-30.md`,
`recon_reference_2026-04-30.md`.
