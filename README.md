# Policy Renewal Agent 🛡️

An AI-powered insurance policy renewal platform built with LangGraph multi-agent orchestration, RAG, and a modern React frontend.

## Features

- **AI Multi-Agent System** — Goal Understanding, Memory, Knowledge (RAG), Recommendation, Notification agents
- **LangGraph Workflow** — Full orchestrated pipeline from login → memory → policy → RAG → recommendation → notification
- **RAG Knowledge Base** — ChromaDB-backed PDF policy document Q&A
- **Policy Dashboard** — View, filter, and manage all insurance policies
- **AI Renewal Recommendations** — Personalized renewal analysis with probability scoring
- **Chat Interface** — Conversational AI assistant powered by GPT-4o
- **Notification Center** — In-app, email, SMS, WhatsApp notifications
- **Admin Dashboard** — Stats, charts, customer/policy/renewal management, PDF upload
- **JWT Auth** — Secure login with role-based access (customer / admin)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Python 3.12, SQLAlchemy, SQLite |
| AI | LangGraph, LangChain, OpenAI GPT-4o |
| RAG | ChromaDB, OpenAI Embeddings |
| Frontend | React 18, TypeScript, Vite, TailwindCSS v4 |
| Charts | Recharts |
| Auth | JWT (python-jose), bcrypt |
| Deploy | Docker, Docker Compose |

## Quick Start

### 1. Clone & Configure

```bash
git clone <repo-url>
cd policy-renewal-agent
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY
```

### 2. Run with Docker

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 3. Run Locally (Development)

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
cp ../.env.example .env       # edit with your keys
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```

### 4. Seed RAG Knowledge Base (Optional)

```bash
cd backend
python ../scripts/generate_pdfs.py        # generates sample policy text files
python ../scripts/seed_rag.py             # ingests them into ChromaDB
```

## Demo Accounts

| Email | Password | Role |
|-------|----------|------|
| admin@insurance.com | admin123 | Admin |
| john.smith@email.com | password123 | Customer |
| sarah.johnson@email.com | password123 | Customer |
| mike.davis@email.com | password123 | Customer |
| emily.chen@email.com | password123 | Customer |

## Project Structure

```
policy-renewal-agent/
├── backend/
│   ├── agents/              # AI agents (goal, memory, knowledge, recommendation, notification)
│   ├── workflows/           # LangGraph orchestrator
│   ├── rag/                 # ChromaDB RAG engine
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # FastAPI routers
│   ├── services/            # Auth, LLM, seed services
│   ├── db/                  # Database setup
│   ├── tests/               # pytest tests
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── pages/           # React pages
│   │   ├── components/      # Shared components
│   │   ├── api/             # API client & services
│   │   ├── store/           # Zustand state
│   │   ├── lib/             # Utilities
│   │   └── types/           # TypeScript types
│   └── tests/
├── scripts/                 # Seed & utility scripts
├── docs/                    # Documentation
├── docker-compose.yml
└── .env.example
```

## Running Tests

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
```

## API Documentation

Interactive Swagger UI available at: http://localhost:8000/docs

See [docs/API.md](docs/API.md) for full reference.
