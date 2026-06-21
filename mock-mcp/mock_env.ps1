# CMA / Claude Managed Agent 端的 MCP 接線(PowerShell)。
# 用法:先 `python mock-mcp/run_all_http.py` 把 server 跑起來,再 `. mock-mcp/mock_env.ps1`
# 這些 env var 就是 cookbook agent.yaml 裡 ${..._MCP_URL} 會去讀的值。
# 全部 mock / dev,指向本機 streamable-http。

$env:GL_MCP_URL        = "http://127.0.0.1:8001/mcp"   # internal-gl  (gl-reconciler, month-end-closer)
$env:SUBLEDGER_MCP_URL = "http://127.0.0.1:8002/mcp"   # subledger    (gl-reconciler)
$env:PORTFOLIO_MCP_URL = "http://127.0.0.1:8003/mcp"   # portfolio    (valuation-reviewer)
$env:NAV_MCP_URL       = "http://127.0.0.1:8004/mcp"   # nav          (statement-auditor)
$env:CRM_MCP_URL       = "http://127.0.0.1:8005/mcp"   # crm          (meeting-prep-agent)
$env:SCREENING_MCP_URL = "http://127.0.0.1:8006/mcp"   # screening    (kyc-screener)
$env:CAPIQ_MCP_URL     = "http://127.0.0.1:8007/mcp"   # capiq        (market-researcher, model-builder, pitch-agent, meeting-prep-agent)

# factset / daloopa:shipped 設定走真實廠商 URL(需金鑰)。要全離線測試再把下面兩行解除註解,
# 並用 `python mock-mcp/run_all_http.py` 啟動到的 8008 / 8009。
# $env:FACTSET_MCP_URL = "http://127.0.0.1:8008/mcp"   # factset (earnings-reviewer, market-researcher)
# $env:DALOOPA_MCP_URL = "http://127.0.0.1:8009/mcp"   # daloopa (earnings-reviewer, model-builder, pitch-agent)

Write-Host "mock MCP env vars set (GL/SUBLEDGER/PORTFOLIO/NAV/CRM/SCREENING/CAPIQ -> 127.0.0.1:8001-8007)."
