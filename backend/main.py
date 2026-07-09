import logging
import os
import ssl
from contextlib import asynccontextmanager

# Disable SSL verification for corporate proxy (tiktoken, urllib downloads)
os.environ.setdefault("PYTHONHTTPSVERIFY", "0")
os.environ.setdefault("CURL_CA_BUNDLE", "")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "")
ssl._create_default_https_context = ssl._create_unverified_context

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db.database import init_db
from routers import auth, customers, policies, renewals, chat, notifications, knowledge, admin, data_management, support
from services.seed import seed_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Policy Renewal Agent API...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/chroma", exist_ok=True)
    os.makedirs("data/pdfs", exist_ok=True)
    init_db()
    await seed_database()
    logger.info("API ready.")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Policy Renewal Agent API",
    description="AI-powered insurance policy renewal agent",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(policies.router, prefix="/api/policies", tags=["policies"])
app.include_router(renewals.router, prefix="/api/renewals", tags=["renewals"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(data_management.router, prefix="/api/data", tags=["data-management"])
app.include_router(support.router, prefix="/api/support", tags=["support"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "Policy Renewal Agent"}
