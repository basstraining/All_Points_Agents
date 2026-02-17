# All Points ATL — Setup Guide

There are two roles: **you** (deploying the demo) and the **prospect** (using it). You do Steps 1–5 once. The prospect just opens a URL.

---

## Your Setup (One-Time)

### Prerequisites

- Python 3.10+
- [Arcade CLI](https://docs.arcade.dev/en/home): `uv tool install arcade-mcp`
- Authenticated: `arcade login`
- Faker library: `pip3 install faker`
- [Anthropic API key](https://console.anthropic.com/)

### Step 1: Generate the Database

```bash
cd All_Points_Agents
python3 setup_database.py
```

Creates `shared/database/allpoints.db` with ~3,000 records of realistic 3PL data. Dates are relative to today so the data always feels current.

To regenerate fresh:
```bash
python3 setup_database.py --reset
```

### Step 2: Deploy MCP Servers to Arcade Cloud

```bash
./deploy.sh
```

Deploys all 6 servers to Arcade's managed infrastructure. They run persistently — no local machine needed.

| Server | Domain | Tools |
|--------|--------|-------|
| carrier_exceptions | Shipment exceptions | 5 |
| email_triage | Email inbox | 4 |
| profitability | Client profitability | 5 |
| rate_shopping | Carrier rate comparison | 5 |
| chargeback_defense | Retailer chargebacks | 5 |
| ltl_automation | LTL freight | 5 |

### Step 3: Create the Arcade Gateway

1. Go to the [Arcade Dashboard](https://arcade.dev) → **MCP Gateways**
2. Create a new Gateway (e.g., name: "AllPoints Demo", slug: "allpoints-demo")
3. Add all 29 tools from the 6 deployed servers
4. Add integrations from the Arcade catalog:
   - **Gmail** — for sending emails
   - **Google Slides** — for building QBR decks
   - **Slack** — for posting team alerts
5. Save — your Gateway URL is:
   ```
   https://api.arcade.dev/mcp/allpoints-demo
   ```

### Step 4: Configure the Chatbot

```bash
cd app
cp .env.example .env
```

Fill in `.env`:
```
ANTHROPIC_API_KEY=sk-ant-...
ARCADE_GATEWAY_URL=https://api.arcade.dev/mcp/allpoints-demo
ARCADE_API_KEY=arc_...
```

Test locally:
```bash
pip install -r requirements.txt
chainlit run main.py
```

### Step 5: Deploy the Chatbot

**Railway (recommended):**
1. Push repo to GitHub
2. Connect the repo in [Railway](https://railway.app)
3. Set the root directory to `app/`
4. Add the 3 env vars from `.env`
5. Railway detects the Procfile and deploys automatically
6. Get your public URL (e.g., `https://allpoints-demo.up.railway.app`)

**Other options:** Render, Fly.io, or any platform that runs Python + exposes a port.

---

## Prospect Experience

The prospect does **zero setup**. They receive a URL.

1. **Open the chatbot link** (e.g., `https://allpoints-demo.up.railway.app`)
2. **Enter their email** — used for per-user Arcade authentication
3. **Start chatting** — all 29 AllPoints tools are live immediately
4. **Authorize personal tools (first time)** — when Claude tries to send an email or post to Slack, Arcade prompts them to authorize Gmail/Slack/Slides via OAuth. One click each.

That's it. No Arcade account setup. No Gateway creation. No Claude.ai subscription.

---

## Running the Demo

See [demo_scenarios.md](demo_scenarios.md) for 7 pre-crafted conversation starters. Recommended order for a live sales call:

1. **Monday Morning Triage** — touches all domains, sets context
2. **Chargeback Sprint** — urgency + email sent to real inbox
3. **Client QBR Deck** — Google Slides artifact delivered
4. **Let them freestyle** — ask "What would you want to know next?"

---

## File Structure

```
All_Points_Agents/
├── app/                             # Hosted chatbot
│   ├── main.py                      # Chainlit app (chat loop + tool calling)
│   ├── gateway.py                   # Arcade Gateway MCP client
│   ├── config.py                    # Settings (env vars)
│   ├── chainlit.md                  # Welcome screen
│   ├── requirements.txt             # Chatbot dependencies
│   ├── Procfile                     # Railway deployment
│   └── .env.example                 # Environment variable template
│
├── shared/                          # Shared database + utilities
│   ├── database/
│   │   ├── schema.sql               # 24 tables
│   │   ├── seed_data.py             # Deterministic data generator
│   │   ├── connection.py            # Thread-safe SQLite helper
│   │   └── allpoints.db             # Generated (gitignored)
│   ├── formatters.py                # JSON/CSV/Markdown output
│   └── constants.py                 # Violation codes, enums
│
├── mcp_servers/                     # Single combined MCP server (29 tools)
│   └── allpoints_server.py          # All 6 domains in one server
│
├── claude_project_prompt.md         # System prompt (loaded by chatbot)
├── demo_scenarios.md                # 7 demo conversation starters
├── deploy.sh                        # Deploy MCP servers to Arcade Cloud
├── setup_database.py                # One-command DB init
└── requirements.txt                 # MCP server dependencies
```

## Troubleshooting

**Chatbot can't connect to Gateway**
Check that `ARCADE_GATEWAY_URL` and `ARCADE_API_KEY` are set correctly in `.env`. Verify the Gateway exists in the Arcade Dashboard.

**Tools not discovered**
Make sure the 6 MCP servers are deployed (`./deploy.sh status`) and added to the Gateway in the Arcade Dashboard.

**OAuth popup doesn't appear**
The prospect needs to trigger a tool that requires auth (e.g., ask Claude to send an email). Arcade triggers OAuth just-in-time on first use.

**Database is empty or missing**
Run `python3 setup_database.py --reset` to regenerate.

**Deploy fails**
Make sure you're authenticated with Arcade: `arcade login`
