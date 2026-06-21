# `mock-mcp/` — 給 10 支 FSI agent 用的本機假 MCP server

這個資料夾放的是**自己跑得起來的 Python MCP server**,用來頂替那 10 支 agent 原本要接的資料來源。每一支都**從本機的 `*.csv` 餵假資料**,所以你**不用真的廠商金鑰、也不用接公司內部系統**,就能把 agent 從頭到尾跑一遍。

> ⚠️ **只給測試／開發用,別上線。** 這裡每個數字都是假的(從 `docs/outputs/<agent>/samples/` 和 agent 原始碼**逆向工程**回來的)。**不要**把正式環境的 agent 接到這上面。另外有幾份資料是**故意埋雷**的(制裁名單命中、估值違反政策、對帳對不起來…),目的是讓你測 agent 的把關有沒有擋下來 — 細節看各 server 自己的 `README.md`。

## 哪支 agent 要哪個 MCP

下表是從**劇本**(`plugins/agent-plugins/<slug>/agents/<slug>.md`)和 **CMA cookbook**(`managed-agent-cookbooks/<slug>/**.yaml`)裡撈出來對照的。

| MCP 資料夾 | server 名稱 | 環境變數 (CMA) | 哪些 agent 會呼叫 |
|---|---|---|---|
| [`internal-gl/`](internal-gl/) | `internal-gl` | `GL_MCP_URL` | gl-reconciler, month-end-closer |
| [`subledger/`](subledger/) | `subledger` | `SUBLEDGER_MCP_URL` | gl-reconciler |
| [`portfolio/`](portfolio/) | `portfolio` | `PORTFOLIO_MCP_URL` | valuation-reviewer |
| [`nav/`](nav/) | `nav` | `NAV_MCP_URL` | statement-auditor |
| [`crm/`](crm/) | `crm` | `CRM_MCP_URL` | meeting-prep-agent |
| [`screening/`](screening/) | `screening` | `SCREENING_MCP_URL` | kyc-screener |
| [`capiq/`](capiq/) | `capiq` | `CAPIQ_MCP_URL` | market-researcher, model-builder, pitch-agent, meeting-prep-agent |
| [`factset/`](factset/) | `factset` | `FACTSET_MCP_URL` | earnings-reviewer, market-researcher |
| [`daloopa/`](daloopa/) | `daloopa` | `DALOOPA_MCP_URL` | earnings-reviewer, model-builder, pitch-agent |

> `factset` / `daloopa` 這兩支,在 `plugins/vertical-plugins/financial-analysis/.mcp.json` 裡本來就有**真實廠商的 URL**。這裡的本機假版本是讓你**沒網路／沒金鑰也能離線跑**;等你拿到金鑰,再換回廠商 URL 就好。
> 另外 7 支在 repo 裡都只是 placeholder（佔位）(只在 `${..._MCP_URL}` 被提到、實際沒定義),所以這裡等於是把「它們到底該做什麼」實作出來當**參考範本**。

## 資料夾長相(每個資料夾都各自獨立)

```
mock-mcp/
├── requirements.txt          # 只有一個相依套件:mcp
├── selftest.py               # 載入每個 CSV、檢查資料對不對 — 不需要裝 SDK
├── README.md                 # 就是這份
└── <name>/
    ├── server.py             # MCP server 本體(FastMCP,預設走 stdio)
    ├── data/*.csv            # 這支 server 餵的假資料
    └── README.md             # 工具清單、資料欄位說明、埋了哪些測試雷
```

這裡**沒有共用程式碼** — 每支 `server.py` 都把讀 CSV 的小工具**自己內含**一份,所以你單獨把某個資料夾複製出去,它照樣跑得起來。

## 安裝

```bash
pip install -r requirements.txt
```

## 跑起 mock server(走 HTTP)

agent 兩個 surface 都接 **HTTP**(streamable-http),所以先把 server 跑起來:

```bash
python3 mock-mcp/run_all_http.py                                 # 一次開全部 9 支(Ctrl+C 收掉)
python3 mock-mcp/run_all_http.py --only internal-gl subledger    # 只開某幾支
```

每支固定一個 port(internal-gl 8001、subledger 8002、portfolio 8003、nav 8004、crm 8005、screening 8006、capiq 8007、factset 8008、daloopa 8009),服務開在 `http://127.0.0.1:<port>/mcp`。

> 想單獨手動測一支:`python3 mock-mcp/internal-gl/server.py --http --port 8001`;或用預設 stdio:`python3 mock-mcp/internal-gl/server.py`。

## 接進 agent(兩個 surface 都已接好)

**Cowork 外掛 — 已內建在各 vertical 的 `.mcp.json`(`type: http`),裝對應 vertical plugin + server 跑起來就連得上:**

| vertical plugin | 接的 mock server |
|---|---|
| `fund-admin` | internal-gl(8001)、subledger(8002)、nav(8004) |
| `private-equity` | portfolio(8003) |
| `wealth-management` | crm(8005) |
| `operations` | screening(8006) |
| `financial-analysis` | capiq(8007)(factset / daloopa 維持真實廠商 URL,未 mock) |

長相(每筆都是 localhost http,不寫死本機路徑):

```jsonc
{ "mcpServers": { "internal-gl": { "type": "http", "url": "http://127.0.0.1:8001/mcp" } } }
```

**CMA cookbook(`${..._MCP_URL}`)— 用附的 env 檔一次設好(yaml 不用動,本來就引用了):**

```bash
source mock-mcp/mock.env          # macOS / Linux / Git Bash
```

```powershell
. mock-mcp/mock_env.ps1           # Windows PowerShell
```

> factset / daloopa 的 `.mcp.json` 與 env 預設走**真實廠商 URL**(需金鑰);要全離線就把 `mock_env` 裡那兩行解除註解,並用 `run_all_http.py` 把 8008 / 8009 跑起來。

## 驗證

```bash
python3 selftest.py            # 一次檢查九支的資料對不對(不用裝 SDK)
```

`selftest.py` 會跑 54 項檢查(CSV 讀得進來 + 埋的測試雷都還在),而且**完全不需要任何相依套件**。想連真的協定一起測,就把 `mcp` 裝起來、隨便挑一支 server 開來打。

> ℹ️ **為什麼叫 `mock-mcp`、不叫 `mcp`?** 如果資料夾叫 `mcp`,只要 repo 根目錄被加進 `sys.path`,它就會把這個資料夾當成 PEP-420 namespace package,**蓋掉你裝的 `mcp` SDK**(例如在根目錄下 `python3 -c "import mcp"` 會 import 到這個資料夾、而不是 SDK)。取名 `mock-mcp` 就完全避開這個坑。
