# AnarockOne Setup With Codex

Use this guide to set up, run, test, and deploy the AnarockOne Relationship Intelligence POC on a new machine using Codex.

## What This Repo Contains

- FastAPI backend with LangServe routes.
- React/Vite frontend in `frontend/`.
- Dummy relationship intelligence data for stakeholders.
- Dockerfile for single-service deployment.
- Render Blueprint config in `render.yaml`.

The production shape is one service: Docker builds the React frontend, copies `frontend/dist` into the Python image, and FastAPI serves both the UI and API.

## Prerequisites

Install:

- Python `3.12`
- Node.js `18+`
- Yarn `1.x`
- Git
- Docker, only if testing container deployment locally

Check versions:

```bash
python3 --version
node --version
yarn --version
git --version
```

## Environment Variables

Create `.env` in the repo root:

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORGANISATION_ID=
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
```

`OPENAI_ORGANISATION_ID` can be empty unless the OpenAI account requires an org value.

Do not commit `.env`.

## Backend Setup

From repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run tests:

```bash
python3 -m pytest
```

Run backend only:

```bash
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Useful endpoints:

```text
GET  http://127.0.0.1:8000/health
POST http://127.0.0.1:8000/relationship-intelligence/invoke
POST http://127.0.0.1:8000/llm-response/invoke
```

Sample API call:

```bash
curl -X POST http://127.0.0.1:8000/relationship-intelligence/invoke \
  -H "Content-Type: application/json" \
  -d '{"input":{"query":"Who has recent context on Radhika?","stakeholder_name":"Radhika"}}'
```

## Frontend Setup

For frontend dev server:

```bash
cd frontend
yarn install --frozen-lockfile
```

Create `frontend/.env` for local dev:

```bash
VITE_RELATIONSHIP_API_URL=http://127.0.0.1:8000/relationship-intelligence/invoke
```

Run frontend:

```bash
yarn dev --port 5173
```

Open:

```text
http://127.0.0.1:5173/
```

The backend must also be running on port `8000`.

## Combined Local Run

To test the deploy-style combined service:

```bash
cd frontend
yarn install --frozen-lockfile
yarn build
cd ..
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

In this mode, FastAPI serves the built React app from `frontend/dist`.

## Docker Local Test

Build:

```bash
docker build -t anarockone .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -e OPENAI_ORGANISATION_ID="$OPENAI_ORGANISATION_ID" \
  -e OPENAI_MODEL="gpt-4o-mini" \
  -e OPENAI_TEMPERATURE="0" \
  anarockone
```

Open:

```text
http://127.0.0.1:8000/
```

## Render Deployment

This repo includes `render.yaml`.

Steps:

1. Push the repo to GitHub.
2. In Render, create a new Blueprint from the GitHub repo.
3. Render reads `render.yaml` and creates the `anarockone` Docker web service.
4. Add environment variables in Render:

```bash
OPENAI_API_KEY=...
OPENAI_ORGANISATION_ID=
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
```

5. Deploy.

Render will provide a URL like:

```text
https://anarockone.onrender.com
```

## Custom Domain

`anarockone.com` requires owning or controlling that domain.

If you own it:

1. Add `anarockone.com` as a custom domain in Render.
2. Render will show DNS records to add.
3. Add those DNS records in the domain registrar or DNS provider.
4. Wait for DNS and TLS provisioning.

If you do not own it, use the Render-provided `.onrender.com` URL for the demo.

## Codex Handoff Prompt

Use this prompt in a fresh Codex session:

```text
You are working in the AnarockOne repo. Read SETUP_WITH_CODEX.md first. Set up the backend and frontend, run tests, build the frontend, and verify the combined FastAPI service serves the UI at / and health at /health. Do not commit .env or generated node_modules/dist artifacts.
```

## Troubleshooting

- If the frontend cannot reach the API in local dev, check `frontend/.env`.
- If `/` returns JSON instead of the UI, build the frontend with `cd frontend && yarn build`, then restart FastAPI.
- If OpenAI returns `insufficient_quota`, the API key/account lacks usable quota.
- If Render free service is slow on first request, it may be spinning up after idle.
- Do not commit `frontend/node_modules/`, `frontend/dist/`, `.env`, or Python cache files.
