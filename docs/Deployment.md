# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- OpenAI API key (or Azure OpenAI credentials)

## Docker Deployment (Recommended)

### 1. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-random-secret-key-min-32-chars
```

### 2. Build and start

```bash
docker-compose up --build -d
```

### 3. Verify

```bash
curl http://localhost:8000/api/health
# {"status":"ok","service":"Policy Renewal Agent"}
```

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### 4. View logs

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Stop

```bash
docker-compose down
```

## Local Development

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp ../.env.example .env   # fill in OPENAI_API_KEY

uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
# Runs on http://localhost:3000
# Proxies /api/* to http://localhost:8000
```

### Seed RAG Knowledge Base

```bash
cd backend
python ../scripts/generate_pdfs.py   # creates sample policy text files
python ../scripts/seed_rag.py        # ingests into ChromaDB
```

## Production Checklist

- [ ] Set strong `SECRET_KEY` (32+ random chars)
- [ ] Set `OPENAI_API_KEY`
- [ ] Restrict CORS origins in `main.py`
- [ ] Use PostgreSQL instead of SQLite for production
- [ ] Set up persistent volume for ChromaDB
- [ ] Configure SMTP for email notifications
- [ ] Enable `LANGCHAIN_TRACING_V2=true` + `LANGCHAIN_API_KEY` for LangSmith monitoring
- [ ] Use HTTPS (reverse proxy with nginx/Caddy)

## Azure OpenAI

Set these in `.env` instead of `OPENAI_API_KEY`:

```
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01
```

## GitHub Actions CI

The workflow at `.github/workflows/ci.yml` runs:
1. Backend pytest on every push
2. Frontend vitest on every push
3. Docker build verification on main branch
