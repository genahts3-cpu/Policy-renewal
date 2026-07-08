# Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Login │ Dashboard │ Policies │ Renewals │ Chat │ Admin      │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JWT)
┌────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                           │
│  /auth  /customers  /policies  /renewals  /chat  /admin     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              LangGraph Workflow Orchestrator                  │
│                                                              │
│  Customer Login                                              │
│       ↓                                                      │
│  Load Customer Memory ──── SQLite (history, claims)          │
│       ↓                                                      │
│  Understand Goal ────────── GPT-4o (intent, urgency)         │
│       ↓                                                      │
│  Retrieve Policy ─────────  SQLite                           │
│       ↓                                                      │
│  Retrieve RAG Context ───── ChromaDB + OpenAI Embeddings     │
│       ↓                                                      │
│  [conditional]                                               │
│  ├── Renewal/Recommend → Renewal Recommendation Agent        │
│  └── Q&A/General      → Policy Knowledge Agent (RAG)         │
│       ↓                                                      │
│  Generate Response ──────── GPT-4o                           │
│       ↓                                                      │
│  Save Conversation ──────── SQLite                           │
│       ↓                                                      │
│  Send Notification ──────── Notification Agent               │
└─────────────────────────────────────────────────────────────┘
```

## AI Agents

### 1. Goal Understanding Agent
- Input: raw customer message
- Uses GPT-4o structured output to extract intent, policy number, urgency
- Intents: `renew_policy`, `ask_question`, `check_status`, `get_recommendation`, `general_chat`

### 2. Customer Memory Agent
- Loads customer profile, all policies, claims history, recent conversations from SQLite
- Builds a context string passed to all downstream agents
- Saves every conversation turn for persistent memory

### 3. Policy Knowledge Agent (RAG)
- Retrieves top-k relevant chunks from ChromaDB using cosine similarity
- Injects context into GPT-4o prompt
- Returns answer + source document names

### 4. Renewal Recommendation Agent
- Analyzes: age, policy type, claims history, risk profile, days until expiry
- Uses GPT-4o structured output → `RenewalRecommendation` Pydantic model
- Returns: probability score, recommended premium, personalized message, key reasons

### 5. Notification Agent
- Generates personalized messages per channel (email, SMS, WhatsApp, in_app)
- Stores notifications in SQLite
- Supports multi-channel delivery

### 6. Workflow Orchestrator (LangGraph)
- StateGraph with typed `AgentState`
- Conditional edges based on detected intent
- Full async execution

## Database Schema

```
customers ──< policies ──< renewals
    │              │
    └──< claims    └──< (policy_id in claims)
    │
    └──< conversations
    │
    └──< notifications
```

## RAG Pipeline

```
PDF/Text → PyPDFLoader → RecursiveCharacterTextSplitter (1000/150)
        → OpenAI Embeddings → ChromaDB (persist)
        → similarity_search(k=4) → context injection → GPT-4o
```

## Security

- JWT tokens (HS256, configurable expiry)
- bcrypt password hashing
- Role-based access: customer vs admin endpoints
- All secrets via `.env` / environment variables
- CORS configured (restrict origins in production)
