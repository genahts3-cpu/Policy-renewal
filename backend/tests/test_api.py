import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///./data/test_policy_renewal.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["OPENAI_API_KEY"] = "sk-test"

from main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_login_admin():
    response = client.post("/api/auth/login", json={"email": "admin@insurance.com", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["is_admin"] is True


def test_login_customer():
    response = client.post("/api/auth/login", json={"email": "john.smith@email.com", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["is_admin"] is False


def test_login_invalid():
    response = client.post("/api/auth/login", json={"email": "wrong@email.com", "password": "wrong"})
    assert response.status_code == 401


def test_get_me():
    login = client.post("/api/auth/login", json={"email": "john.smith@email.com", "password": "password123"})
    token = login.json()["access_token"]
    response = client.get("/api/customers/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "john.smith@email.com"


def test_get_policies():
    login = client.post("/api/auth/login", json={"email": "john.smith@email.com", "password": "password123"})
    token = login.json()["access_token"]
    response = client.get("/api/policies/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_notifications():
    login = client.post("/api/auth/login", json={"email": "john.smith@email.com", "password": "password123"})
    token = login.json()["access_token"]
    response = client.get("/api/notifications/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_admin_stats():
    login = client.post("/api/auth/login", json={"email": "admin@insurance.com", "password": "admin123"})
    token = login.json()["access_token"]
    response = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_customers" in data
    assert "total_policies" in data


def test_admin_access_denied():
    login = client.post("/api/auth/login", json={"email": "john.smith@email.com", "password": "password123"})
    token = login.json()["access_token"]
    response = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_unread_notifications():
    login = client.post("/api/auth/login", json={"email": "john.smith@email.com", "password": "password123"})
    token = login.json()["access_token"]
    response = client.get("/api/notifications/unread-count", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "count" in response.json()
