# 🚀 n8n Production Deployment Guide for CyberRant

## How It Works in Production

```
┌──────────────────────────────────────────────────────────────┐
│                    RENDER.COM                                 │
│                                                              │
│  ┌─────────────────┐    Webhook     ┌─────────────────┐     │
│  │  rant-backend    │ ──────────── →│   rant-n8n       │     │
│  │  (FastAPI)       │               │   (n8n Engine)   │     │
│  │  Port: 8000      │← JSON Result ─│   Port: 5678     │     │
│  └───────┬─────────┘               └───────┬─────────┘     │
│          │                                  │               │
│          │  SQL Queries                     │  SQL Queries   │
│          │                                  │               │
│  ┌───────▼──────────────────────────────────▼─────────┐     │
│  │              cyberrant-db (PostgreSQL)              │     │
│  │  user_posts | community_intel | trend_history       │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## Step-by-Step Deployment

### Step 1: Push Code to GitHub

Make sure your repo has this structure:
```
CyberRant/
├── Dockerfile            ← Backend Dockerfile (already exists)
├── render.yaml           ← Render Blueprint (just created)
├── n8n/
│   └── Dockerfile        ← n8n Dockerfile (just created)
├── n8n_rant_ai_intel.json ← n8n Workflow Export
├── backend/
│   ├── main.py
│   ├── services/
│   │   └── n8n_webhook.py ← Webhook Bridge (just created)
│   └── ...
└── frontend/
    └── ...
```

Push to GitHub:
```bash
git add .
git commit -m "feat: add n8n production deployment config"
git push origin main
```

### Step 2: Deploy on Render (One-Click)

1. Go to **https://dashboard.render.com**
2. Click **"New"** → **"Blueprint"**
3. Connect your **GitHub repo** (CyberRant)
4. Render reads `render.yaml` and auto-creates:
   - `rant-backend` (Web Service)
   - `rant-n8n` (Web Service)
   - `cyberrant-db` (PostgreSQL)
   - `n8n-db` (PostgreSQL)
5. Click **"Apply"**

### Step 3: Set Secret Environment Variables

In Render Dashboard, manually set these for each service:

**rant-backend:**
| Key | Value |
|-----|-------|
| `OPENROUTER_API_KEY` | `sk-or-v1-...` |
| `N8N_WEBHOOK_URL` | `https://rant-n8n.onrender.com` |

**rant-n8n:**
| Key | Value |
|-----|-------|
| `N8N_BASIC_AUTH_USER` | `admin` |
| `N8N_BASIC_AUTH_PASSWORD` | Your strong password |
| `WEBHOOK_URL` | `https://rant-n8n.onrender.com/` |
| `OPENROUTER_API_KEY` | `sk-or-v1-...` |

### Step 4: Initialize Database Schema

After Render deploys the PostgreSQL database:

1. Go to **cyberrant-db** in Render Dashboard
2. Click **"Shell"** tab
3. Paste the contents of `backend/community_intel_schema.sql`
4. Execute

### Step 5: Import n8n Workflow

1. Open `https://rant-n8n.onrender.com` in browser
2. Login with your Basic Auth credentials
3. Click **"Workflows"** → **"Import from File"**
4. Upload `n8n_rant_ai_intel.json`
5. **Configure Credentials:**
   - Create a **PostgreSQL** credential using `APP_DB_*` env vars
   - Create an **HTTP Header Auth** credential with `OPENROUTER_API_KEY`
6. **Activate** the workflow (toggle ON)

### Step 6: Verify Production

```bash
# Test Backend Health
curl https://rant-backend.onrender.com/ping

# Test Intelligence API
curl https://rant-backend.onrender.com/api/intelligence

# Test n8n Health
curl -u admin:yourpassword https://rant-n8n.onrender.com/healthz
```

## How the Connection Works in Production

1. **User interacts** with frontend at `https://rant-backend.onrender.com`
2. **Agent executes** → LEA returns result to backend
3. **Backend fires webhook** → `POST https://rant-n8n.onrender.com/webhook/agent-enrich`
4. **n8n processes** → Enriches data with LLM → Stores in PostgreSQL
5. **Frontend reads** → `GET /api/intelligence` → Shows trending data
6. **Cron runs** → Every 30 min, n8n also runs batch analytics independently

## Troubleshooting

| Issue | Solution |
|-------|---------|
| n8n shows "Waiting for webhook" | Workflow is ready. Backend will trigger it on execution. |
| 502 Bad Gateway on n8n | Check if PORT env var is set to `5678` |
| Workflows lost after redeploy | Ensure Render Disk is mounted at `/home/node/.n8n` |
| Backend can't reach n8n | Verify `N8N_WEBHOOK_URL` env var in rant-backend |
| Free tier sleeps after 15min | Upgrade to Starter plan ($7/mo) for always-on |
