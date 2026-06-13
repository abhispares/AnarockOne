# AnarockOne Relationship Intelligence

FastAPI + React POC for an AI-powered Relationship Intelligence Platform using the same LangServe runnable pattern used in `anarock.genie`.

The POC uses seeded dummy data for BD Tracker updates, Microsoft Teams meetings, and Outlook emails. Queries are answered by an LLM using only that dummy relationship context.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Add your OpenAI API key in `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_ORGANISATION_ID=
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
```

## Run

```bash
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

For local frontend-only development:

```bash
cd frontend
yarn install
yarn dev --port 5173
```

## Deploy

This repo is prepared for a single Render web service deploy. The Dockerfile builds the React frontend and serves it from FastAPI.

1. Push this repo to GitHub.
2. In Render, create a new Blueprint from `render.yaml`, or create a Docker Web Service manually.
3. Set these environment variables in Render:

```bash
OPENAI_API_KEY=...
OPENAI_ORGANISATION_ID=
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0
```

4. Deploy the service. Render will provide a URL like `https://anarockone.onrender.com`.
5. To use `anarockone.com`, you must own/control that domain and add it as a custom domain in Render DNS settings.

## APIs

Health check:

```bash
curl http://127.0.0.1:8000/health
```

LLM response:

```bash
curl -X POST http://127.0.0.1:8000/llm-response/invoke \
  -H "Content-Type: application/json" \
  -d '{"input":{"input":"Write a short greeting"}}'
```

Relationship intelligence query:

```bash
curl -X POST http://127.0.0.1:8000/relationship-intelligence/invoke \
  -H "Content-Type: application/json" \
  -d '{"input":{"query":"Who has recently interacted with Abhishek and what should I know before outreach?"}}'
```

Optional stakeholder filter:

```bash
curl -X POST http://127.0.0.1:8000/relationship-intelligence/invoke \
  -H "Content-Type: application/json" \
  -d '{"input":{"stakeholder_name":"Nidhi","query":"What are Nidhi's concerns and who can give me a warm intro?"}}'
```
