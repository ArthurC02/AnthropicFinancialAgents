# -*- coding: utf-8 -*-
"""Start every mock-mcp server in streamable-http mode, one per port.

The agents wire to MCP over HTTP on both surfaces:
  - Cowork plugin  : plugins/vertical-plugins/<vertical>/.mcp.json  -> type: http
  - CMA cookbook   : ${..._MCP_URL} env vars (see mock_env.ps1 / mock.env)
Both point at the same http://127.0.0.1:<port>/mcp this launcher serves.

Usage:
    python mock-mcp/run_all_http.py            # start all 9 servers, Ctrl+C to stop
    python mock-mcp/run_all_http.py --only internal-gl subledger

Mock / dev only. Each server reads its own ./data/*.csv.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# name -> port  (must match each server's DEFAULT_PORT and the URLs in the
# vertical .mcp.json files / the *_MCP_URL env files)
SERVERS = {
    "internal-gl": 8001,
    "subledger": 8002,
    "portfolio": 8003,
    "nav": 8004,
    "crm": 8005,
    "screening": 8006,
    "capiq": 8007,
    "factset": 8008,
    "daloopa": 8009,
}


def main():
    ap = argparse.ArgumentParser(description="run all mock-mcp servers over streamable-http")
    ap.add_argument("--only", nargs="*", metavar="NAME",
                    help="start only these servers (default: all)")
    args = ap.parse_args()

    names = args.only or list(SERVERS)
    unknown = [n for n in names if n not in SERVERS]
    if unknown:
        sys.exit(f"unknown server(s): {', '.join(unknown)} — valid: {', '.join(SERVERS)}")

    env = dict(os.environ, PYTHONUTF8="1")
    procs = []
    for name in names:
        port = SERVERS[name]
        server = os.path.join(HERE, name, "server.py")
        p = subprocess.Popen([sys.executable, server, "--http", "--port", str(port)], env=env)
        procs.append((name, port, p))
        print(f"  started {name:12} -> http://127.0.0.1:{port}/mcp  (pid {p.pid})")

    print(f"\n{len(procs)} mock MCP server(s) running. Press Ctrl+C to stop them all.\n")
    try:
        while True:
            time.sleep(1)
            for name, port, p in procs:
                if p.poll() is not None:
                    print(f"  ! {name} (:{port}) exited with code {p.returncode}")
    except KeyboardInterrupt:
        print("\nstopping...")
    finally:
        for name, port, p in procs:
            if p.poll() is None:
                p.terminate()
        for name, port, p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        print("all stopped.")


if __name__ == "__main__":
    main()
