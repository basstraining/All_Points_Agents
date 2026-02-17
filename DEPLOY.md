# Deploying the All Points Chatbot

This covers how to get the chatbot running publicly so you can share a URL with prospects.

---

## Option A: Replit

Run and deploy the chatbot on [Replit](https://replit.com). The repo includes a `.replit` config so Replit knows how to run the app.

### 1. Import the project

**Import the entire repo** (the full `All_Points_Agents` folder), not just the `app/` folder. The run config (`.replit`) and the system prompt file (`claude_project_prompt.md`) live at the repo root; the app expects that structure.

1. Go to [replit.com](https://replit.com) and sign in.
2. **Create Repl** → **Import from GitHub** (or upload the project).
3. If using GitHub: paste your **repository** URL and click **Import** so the full repo is cloned.

### 2. Set secrets (environment variables)

1. In Replit, open **Tools** → **Secrets** (or the lock icon).
2. Add:

| Key | Value |
|-----|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (`sk-ant-...`) |
| `ARCADE_GATEWAY_URL` | Your Gateway URL (`https://api.arcade.dev/mcp/allpoints-demo`) |
| `ARCADE_API_KEY` | Your Arcade API key (`arc_...`) |

Replit injects these as environment variables; the app reads them via `config.py`.

### 3. Run the app

1. Click **Run**. Replit will `pip install -r app/requirements.txt` and start Chainlit on port 8080.
2. The app will open in the built-in browser (or use the Webview tab). The URL is your Replit host (e.g. `https://your-repl-name.your-username.repl.co`).

### 4. Deploy to get a permanent URL (optional)

1. In Replit, open **Deploy** (or **Tools** → **Deploy**).
2. Follow the flow to deploy (e.g. to Replit’s Cloud Run–backed hosting).
3. Use the generated URL to share with prospects.

### 5. Share with prospects

Send them the Replit URL (run URL or deployed URL). They open it, enter their email, and start chatting.

**Note:** On the free tier the repl may sleep after inactivity; when someone opens the link it may take a short time to wake. For always-on demos, use a paid Replit plan or another host (e.g. Railway).

---

## Option B: Railway

Railway auto-detects the Procfile, handles Python builds, and gives you a public URL. ~$5/mo for a hobby project, always-on.

### 1. Push to GitHub

```bash
cd All_Points_Agents
git init
git add -A
git commit -m "Initial commit"
gh repo create allpoints-demo --private --push
```

### 2. Create Railway Project

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select your `allpoints-demo` repo
3. When prompted, set the **root directory** to `app/`
4. Click **Add Variables** and add:

| Variable | Value |
|----------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (`sk-ant-...`) |
| `ARCADE_GATEWAY_URL` | Your Gateway URL (`https://api.arcade.dev/mcp/allpoints-demo`) |
| `ARCADE_API_KEY` | Your Arcade API key (`arc_...`) |

5. Click **Deploy**

Railway reads the `Procfile` and runs `chainlit run main.py --host 0.0.0.0 --port $PORT`.

### 3. Generate a Public URL

1. Go to your service in Railway → **Settings** → **Networking**
2. Click **Generate Domain**
3. You'll get something like: `allpoints-demo-production.up.railway.app`
4. Optionally, add a custom domain (e.g., `demo.allpointsatl.com`)

### 4. Share With Prospects

Send them:
- The URL
- The [USAGE.md](USAGE.md) guide (or copy the key parts into an email)

That's it. They open the link, enter their email, and start chatting.

### Managing the Deployment

**View logs:**
Railway dashboard → your service → **Deployments** → click the active deployment → **View Logs**

**Redeploy after changes:**
Push to GitHub. Railway auto-deploys on every push to `main`.

**Regenerate demo data:**
If dates get stale (data is relative to today, so it stays fresh for weeks), run `python3 setup_database.py --reset` locally, then redeploy the MCP servers with `./deploy.sh`.

**Pause/unpause:**
Railway dashboard → your service → **Settings** → **Pause Service** (stops billing when not in use).

---

## Option C: Render

Similar to Railway. Free tier available but the app sleeps after 15 minutes of inactivity (30-second cold start when a prospect opens it — not ideal for a sales demo).

1. Go to [render.com](https://render.com) → **New Web Service** → connect your GitHub repo
2. Set:
   - **Root directory:** `app`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `chainlit run main.py --host 0.0.0.0 --port $PORT`
3. Add environment variables (same 3 as above)
4. Deploy

---

## Option D: Fly.io

Container-based, global edge deployment. Good if you need low latency for international prospects.

```bash
cd app
fly launch
fly secrets set ANTHROPIC_API_KEY=sk-ant-... ARCADE_GATEWAY_URL=https://... ARCADE_API_KEY=arc_...
fly deploy
```

---

## Option E: Run Locally (for testing or live demos)

```bash
cd app
cp .env.example .env
# Fill in your keys in .env

pip install -r requirements.txt
chainlit run main.py
```

Opens at `http://localhost:8000`. Good for testing before deploying, or for running a live demo from your own machine during a sales call.

---

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Railway hosting | ~$5/mo | Can pause when not demoing |
| Anthropic API | Usage-based | ~$0.01-0.05 per conversation turn with Sonnet |
| Arcade Gateway | Check your plan | MCP server hosting + OAuth routing |
| **Total per demo** | **< $1** | A full 30-min prospect session |

---

## What the Prospect Sees

```
1. Opens URL in any browser
           ↓
2. Sees welcome screen + "Enter your email"
           ↓
3. Types email → chatbot connects (2-3 seconds)
           ↓
4. "Connected — 29 tools available. How can I help?"
           ↓
5. Prospect asks questions, gets answers with live data
           ↓
6. When AI sends an email → "Click to authorize Gmail" → one click
           ↓
7. Email lands in their real inbox
```

No downloads. No accounts. No configuration. Just a URL.
