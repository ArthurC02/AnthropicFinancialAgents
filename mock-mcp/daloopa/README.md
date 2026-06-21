# `daloopa` — Granular as-reported line items (mock, read-only)

Stands in for the `daloopa` MCP (`DALOOPA_MCP_URL`). **daloopa has a real vendor URL**
in `plugins/vertical-plugins/financial-analysis/.mcp.json` — this local mock just lets
the agents run offline.

- **Used by:** `earnings-reviewer`, `model-builder`, `pitch-agent`
- **Default HTTP port:** `8009`
- **Run:** `python3 server.py` (stdio) · `python3 server.py --http --port 8009`

## Tools

| Tool | Purpose |
|---|---|
| `list_coverage()` | Tickers / periods / statement groups |
| `get_line_items(ticker, period?, statement?)` | Granular line items, filterable by statement group |

## Data

- **TSM** Q1-2026: revenue mix by **platform** (HPC 61%, Smartphone 26%, …) and by
  **node** (N3 25%, N5 36%, 7nm 13%, advanced ≤7nm 74%), income-statement detail,
  and FY2026 capex guidance — feeds the earnings-reviewer revenue-mix block.
- **VRT** FY2025: **segment** (Americas/APAC/EMEA) and **product** (Power / Thermal
  Management / Rack / Services) revenue, plus backlog $15bn — feeds the model-builder
  and pitch-agent VRT build.

Statement groups: `revenue_mix_platform`, `revenue_mix_node`, `income_statement`,
`guidance`, `segment_revenue`, `product_revenue`, `balance_sheet`.

Source: `docs/outputs/earning-reviewer/scripts/build_tsmc_model.py` (mix blocks),
`docs/outputs/model-builder/note.md`, `docs/outputs/pitch/note.md`.
