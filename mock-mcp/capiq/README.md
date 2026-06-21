# `capiq` — Market data: comps, quotes, events, estimates (mock, read-only)

Stands in for the `capiq` MCP (`CAPIQ_MCP_URL`).

- **Used by:** `market-researcher`, `model-builder`, `pitch-agent`, `meeting-prep-agent`
- **Default HTTP port:** `8007`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8007`

## Tools

| Tool | Purpose |
|---|---|
| `get_comps(sector?, tickers?)` | Peer set with consistent metric definitions |
| `get_quote(ticker)` | Price, market cap, 52-week range |
| `get_market_events(ticker?)` | Recent market events |
| `get_estimates(ticker, period?)` | Forward street estimates |

## Data

- `comps.csv` — **14 names** in AI data-center cooling (VRT, NVT, SU.PA, SMCI, PH,
  FLEX, Delta, Auras, AVC, Wiwynn, Sunon, Lotes, Envicool, Asetek). `n/a` where the
  free source lacks a figure — exactly as in the market-researcher comps workbook.
- `quotes.csv` — VRT, TSM, NVDA, AAPL, MSFT (directional prices).
- `market_events.csv`, `estimates.csv` — VRT / TSM / NVDA forward context.

> ⚠️ Prices and multiples are **synthetic and directional**. `EV/Rev` is not comparable
> across component vs ODM/OEM business models (the comps tool returns this caveat).
> Outliers to flag: Envicool ~77x fwd P/E, Delta +454% 1-yr, SMCI −36%, VRT ~51x EV/EBITDA.

Source: `docs/outputs/market-researcher/scripts/build_comps.py`,
`docs/outputs/*/note.md`.
