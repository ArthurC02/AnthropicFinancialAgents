# `factset` — Fundamentals / consensus / prices (mock, read-only)

Stands in for the `factset` MCP (`FACTSET_MCP_URL`). **factset has a real vendor URL**
in `plugins/vertical-plugins/financial-analysis/.mcp.json` — this local mock just lets
the agents run offline.

- **Used by:** `earnings-reviewer`, `market-researcher`
- **Default HTTP port:** `8008`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8008`

## Tools

| Tool | Purpose |
|---|---|
| `list_coverage()` | Tickers / periods available |
| `get_fundamentals(ticker, period?)` | Reported actuals (long format) |
| `get_consensus_estimates(ticker, period?)` | Consensus vs actual vs prior guidance |
| `get_prices(ticker)` | Recent closes with context |

## Data

- **TSM** Q1-2026 actuals (revenue US$35.9bn, GM 66.2%, EPS NT$22.08 / ADR US$3.49)
  + FY2025 base US$124bn, drives the earnings-reviewer beat/miss workpaper.
- **VRT** FY2025 fundamentals for the model-builder / market-researcher comp work.
- Consensus shows the **beats**: revenue +1.1%, GM +220bps, EPS +5.7% vs street; Q2
  guidance 39.0–40.2 vs consensus 38.1.

Source: `docs/outputs/earning-reviewer/scripts/build_tsmc_model.py` (Q1'26 actual +
variance sheet), `docs/outputs/market-researcher/scripts/build_comps.py`.
