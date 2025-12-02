"""Integration tests for API endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core import auth
from pathlib import Path
import tempfile
import shutil
import os


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def temp_auth_db(monkeypatch):
    """Create a temporary auth database for testing"""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "auth.db"
    
    # Monkeypatch the database path
    original_path = auth.USERS_DB_PATH
    monkeypatch.setattr(auth, "USERS_DB_PATH", db_path)
    
    yield db_path
    
    # Cleanup
    if db_path.exists():
        db_path.unlink()
    shutil.rmtree(temp_dir)
    monkeypatch.setattr(auth, "USERS_DB_PATH", original_path)


@pytest.fixture
def test_user(temp_auth_db):
    """Create a test user and return credentials"""
    user = auth.create_user(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "user_id": user["user_id"]
    }


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_root_endpoint(self, client):
        """Test root health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "ok"

    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestAuthEndpoints:
    """Tests for authentication endpoints"""

    def test_signup_success(self, temp_auth_db, client):
        """Test successful user signup"""
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "password123",
                "full_name": "New User"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert data["email"] == "newuser@example.com"

    def test_signup_duplicate_email(self, temp_auth_db, client):
        """Test signup with duplicate email"""
        # Create first user
        client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        # Try to create duplicate
        response = client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "password456"
            }
        )
        assert response.status_code == 400

    def test_login_success(self, temp_auth_db, client, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": test_user["password"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["email"] == test_user["email"]

    def test_login_wrong_password(self, temp_auth_db, client, test_user):
        """Test login with wrong password"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user["email"],
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 401


