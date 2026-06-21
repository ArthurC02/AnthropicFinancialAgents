# -*- coding: utf-8 -*-
"""Tiny stdio MCP client used to *actually run* the mock-mcp servers.

This is the harness behind every agent run captured under docs/outputs/mcpBased/.
It spawns a mock-mcp `server.py` over stdio (exactly how Claude Code / Cowork
launch an MCP server), performs the real MCP `initialize` + `list_tools` +
`call_tool` round-trip, and snapshots each tool response to JSON.

Two ways to use it
------------------
1) One-off (prints JSON to stdout):
     python mcp_client.py <server.py> <tool_name> '<json-args>'   # path repo-relative
   e.g.
     python mcp_client.py mock-mcp/screening/server.py screen_name '{"name":"Ivan Petrov","dob":"1970-03-15","country":"Russia"}'

2) Batch (spawns the server ONCE, runs many calls, writes one file per call):
     python mcp_client.py --spec spec.json
     python mcp_client.py --spec -        # read the spec from stdin
   spec.json (paths are repo-relative; resolved against the repo root):
     {
       "server": "mock-mcp/internal-gl/server.py",
       "out_dir": "docs/outputs/mcpBased/month-end-closer/mcp_pulls",
       "calls": [
         {"tool": "list_entities", "args": {}, "save_as": "01_list_entities"},
         {"tool": "get_trial_balance",
          "args": {"entity": "Aurora Capital Management LLC", "period": "2026-04"},
          "save_as": "02_trial_balance"}
       ]
     }

   For each call it writes `<out_dir>/<save_as>.json` holding:
     {"server","tool","args","ok","result"|"error"}
   and it also writes `<out_dir>/_tools.json` (the server's advertised tool list).

Mock / dev only. Pure-SDK; no third-party deps beyond `mcp`.
"""
from __future__ import annotations

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Windows already defaults to the Proactor event loop (required for asyncio
# subprocess / the stdio transport) on Python 3.8+, so no policy override is needed.

HERE = os.path.dirname(os.path.abspath(__file__))
# _harness -> mcpBased -> outputs -> docs -> repo root
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def _resolve(path):
    """Resolve a spec path: keep absolute as-is, else treat it as repo-relative.

    Lets pull specs use portable, repo-relative paths (e.g.
    "mock-mcp/internal-gl/server.py" / "docs/outputs/mcpBased/<agent>/mcp_pulls")
    that work from any working directory and carry no machine-specific prefix.
    """
    if not path:
        return path
    return path if os.path.isabs(path) else os.path.join(REPO_ROOT, path)


# Tools whose declared return type is `list`. FastMCP emits ONE content block per
# list element (and no structuredContent), so an N-element list arrives as N blocks
# while a dict — or a 1-element list — arrives as a single block. We can't tell a
# dict from a 1-element list by shape alone, so we name the list tools explicitly to
# reconstruct the right container. Keep this in sync with the @mcp.tool signatures.
_LIST_TOOLS = {
    "get_journal_entries",          # internal-gl
    "get_pending_settlements", "get_fx_rates",                       # subledger
    "get_capital_flows", "get_valuation_policy",                     # portfolio
    "list_clients", "get_open_items", "get_recent_communications",   # crm
    "get_market_events",                                            # crm + capiq
    "get_sanctions_list", "get_pep_list",                           # screening
    "get_estimates",                                               # capiq
    "get_fundamentals", "get_consensus_estimates", "get_prices",    # factset
    "get_line_items",                                              # daloopa
}


def _parse(text):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return text


def _extract(result, tool_name=""):
    """Pull the real Python value back out of an MCP CallToolResult.

    FastMCP serialises each return value as JSON text content blocks. A dict is one
    block; a list is one block PER element. We reassemble the list for known
    list-returning tools so a 1-element list does not collapse into a bare dict.
    """
    sc = getattr(result, "structuredContent", None)
    if isinstance(sc, dict):
        return sc["result"] if set(sc.keys()) == {"result"} else sc

    blocks = [b for b in (getattr(result, "content", []) or []) if getattr(b, "text", None) is not None]
    values = [_parse(b.text) for b in blocks]
    if tool_name in _LIST_TOOLS:
        # A single block may itself already be a JSON list (e.g. an empty list "[]").
        if len(values) == 1 and isinstance(values[0], list):
            return values[0]
        return values
    if not values:
        return None
    return values[0] if len(values) == 1 else values


async def run_batch(server_path, calls, out_dir=None):
    server_abs = _resolve(server_path)
    server_name = os.path.basename(os.path.dirname(server_abs))
    out_dir = _resolve(out_dir)
    params = StdioServerParameters(command=sys.executable, args=[server_abs])
    outputs = []
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_list = [{"name": t.name, "description": (t.description or "").strip().splitlines()[0]
                          if t.description else ""} for t in tools.tools]
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
                with open(os.path.join(out_dir, "_tools.json"), "w", encoding="utf-8") as f:
                    json.dump({"server": server_name, "tools": tool_list},
                              f, ensure_ascii=False, indent=2)
            for c in calls:
                tool, args = c["tool"], c.get("args", {})
                rec = {"server": server_name, "tool": tool, "args": args}
                try:
                    res = await session.call_tool(tool, args)
                    rec["ok"] = not res.isError
                    rec["result"] = _extract(res, tool)
                except Exception as e:  # noqa: BLE001 - surface any call failure into the record
                    rec["ok"] = False
                    rec["error"] = f"{type(e).__name__}: {e}"
                if out_dir and "save_as" in c:
                    path = os.path.join(out_dir, f"{c['save_as']}.json")
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(rec, f, ensure_ascii=False, indent=2)
                    rec["_written"] = path
                outputs.append(rec)
    return tool_list, outputs


def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--spec":
        src = sys.argv[2] if len(sys.argv) > 2 else "-"
        spec = json.load(sys.stdin) if src == "-" else json.load(open(src, encoding="utf-8"))
        tool_list, outputs = asyncio.run(
            run_batch(spec["server"], spec.get("calls", []), spec.get("out_dir"))
        )
        summary = {"server": spec["server"], "tools": [t["name"] for t in tool_list],
                   "calls": [{"tool": o["tool"], "ok": o.get("ok"),
                              "written": os.path.basename(o.get("_written", "")) or None}
                             for o in outputs]}
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    server_path, tool = sys.argv[1], sys.argv[2]
    args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    _, outputs = asyncio.run(run_batch(server_path, [{"tool": tool, "args": args}]))
    print(json.dumps(outputs[0].get("result", outputs[0]), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
