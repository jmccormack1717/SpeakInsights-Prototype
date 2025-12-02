"""Tests for authentication functions"""
import pytest
from app.core import auth
from pathlib import Path
import tempfile
import shutil
import os


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


class TestPasswordHashing:
    """Tests for password hashing functions"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = auth._hash_password(password)
        
        assert "$" in hashed
        assert len(hashed) > 20  # Should have salt + hash

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = auth._hash_password(password)
        
        assert auth._verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = auth._hash_password(password)
        
        assert auth._verify_password(wrong_password, hashed) is False

    def test_hash_password_deterministic_with_salt(self):
        """Test that same password with same salt produces same hash"""
        password = "test_password"
        salt = "test_salt_12345"
        
        hash1 = auth._hash_password(password, salt)
        hash2 = auth._hash_password(password, salt)
        
        assert hash1 == hash2


class TestUserManagement:
    """Tests for user creation and retrieval"""

    def test_create_user(self, temp_auth_db):
        """Test creating a new user"""
        user = auth.create_user(
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        assert user["email"] == "test@example.com"
        assert user["full_name"] == "Test User"
        assert "user_id" in user
        assert user["user_id"] is not None

    def test_create_user_duplicate_email(self, temp_auth_db):
        """Test that creating duplicate user raises error"""
        auth.create_user(
            email="test@example.com",
            password="password123"
        )
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            auth.create_user(
                email="test@example.com",
                password="password456"
            )

    def test_get_user_by_email(self, temp_auth_db):
        """Test retrieving user by email"""
        created = auth.create_user(
            email="test@example.com",
            password="password123",
            full_name="Test User"
        )
        
        retrieved = auth.get_user_by_email("test@example.com")
        
        assert retrieved is not None
        assert retrieved["email"] == "test@example.com"
        assert retrieved["full_name"] == "Test User"
        assert "password_hash" in retrieved

    def test_get_user_by_email_not_found(self, temp_auth_db):
        """Test retrieving non-existent user"""
        retrieved = auth.get_user_by_email("nonexistent@example.com")
        
        assert retrieved is None

    def test_authenticate_user_success(self, temp_auth_db):
        """Test successful authentication"""
        auth.create_user(
            email="test@example.com",
            password="password123"
        )
        
        user = auth.authenticate_user("test@example.com", "password123")
        
        assert user is not None
        assert user["email"] == "test@example.com"
        assert "password_hash" not in user  # Should be removed

    def test_authenticate_user_wrong_password(self, temp_auth_db):
        """Test authentication with wrong password"""
        auth.create_user(
            email="test@example.com",
            password="password123"
        )
        
        user = auth.authenticate_user("test@example.com", "wrong_password")
        
        assert user is None

    def test_authenticate_user_not_found(self, temp_auth_db):
        """Test authentication with non-existent user"""
        user = auth.authenticate_user("nonexistent@example.com", "password123")
        
        assert user is None


class TestJWT:
    """Tests for JWT token creation and validation"""

    def test_create_access_token(self, monkeypatch):
        """Test creating JWT access token"""
        # Set a test secret
        monkeypatch.setattr(auth.settings, "jwt_secret", "test_secret_key")
        monkeypatch.setattr(auth.settings, "jwt_algorithm", "HS256")
        
        data = {"sub": "user123", "email": "test@example.com"}
        token = auth.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token(self, monkeypatch):
        """Test decoding JWT access token"""
        # Set a test secret
        monkeypatch.setattr(auth.settings, "jwt_secret", "test_secret_key")
        monkeypatch.setattr(auth.settings, "jwt_algorithm", "HS256")
        
        data = {"sub": "user123", "email": "test@example.com"}
        token = auth.create_access_token(data)
        
        decoded = auth.decode_access_token(token)
        
        assert decoded["sub"] == "user123"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded


