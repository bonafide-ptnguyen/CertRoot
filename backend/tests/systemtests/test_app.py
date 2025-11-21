import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime, timedelta
import jwt
import io
from bson import ObjectId

# Add backend directory to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

# Now import from app (which is in backend/)
from app import app, SECRET_KEY, ALGORITHM, hash_password, verify_password, create_access_token


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_admin():
    """Mock admin user data"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "username": "testadmin",
        "password": hash_password("testpass123"),
        "email": "admin@test.com",
        "full_name": "Test Admin",
        "created_at": datetime.utcnow(),
        "is_active": True
    }


@pytest.fixture
def valid_token(mock_admin):
    """Generate valid JWT token"""
    return create_access_token(str(mock_admin["_id"]))


@pytest.fixture
def expired_token(mock_admin):
    """Generate expired JWT token"""
    return create_access_token(str(mock_admin["_id"]), expires_delta=timedelta(seconds=-1))


@pytest.fixture
def mock_file():
    """Create mock file for upload"""
    content = b"test file content"
    return ("test.txt", io.BytesIO(content), "text/plain")


@pytest.fixture
def mock_db_collection():
    """Mock MongoDB collection"""
    mock_col = Mock()
    mock_col.find_one = Mock()
    mock_col.insert_one = Mock()
    mock_col.create_index = Mock()
    return mock_col


# ============= HELPER FUNCTION TESTS =============


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")
    
    def test_verify_password_success(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_failure(self):
        """Test password verification with wrong password"""
        password = "testpassword123"
        hashed = hash_password(password)
        
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        admin_id = "test_admin_id_123"
        token = create_access_token(admin_id)
        
        assert token is not None
        assert len(token) > 0
        
        # Decode and verify
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["admin_id"] == admin_id
        assert "exp" in payload


# ============= ADMIN REGISTRATION TESTS =============


class TestAdminRegistration:
    """Test admin registration endpoint"""
    
    @patch("app.get_admin_collection")
    def test_register_admin_success(self, mock_get_col, client, mock_db_collection):
        """Test successful admin registration"""
        mock_db_collection.find_one.return_value = None
        mock_db_collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        mock_get_col.return_value = mock_db_collection
        
        response = client.post(
            "/admin/register",
            params={
                "username": "newadmin",
                "password": "password123",
                "email": "new@test.com",
                "full_name": "New Admin"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "admin_id" in data
        mock_db_collection.insert_one.assert_called_once()
    
    @patch("app.get_admin_collection")
    def test_register_admin_already_exists(self, mock_get_col, client, mock_db_collection, mock_admin):
        """Test registration with existing username"""
        mock_db_collection.find_one.return_value = mock_admin
        mock_get_col.return_value = mock_db_collection
        
        response = client.post(
            "/admin/register",
            params={
                "username": "testadmin",
                "password": "password123",
                "email": "test@test.com",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_register_admin_short_username(self, mock_get_col, client):
        """Test registration with too short username"""
        response = client.post(
            "/admin/register",
            params={
                "username": "ab",
                "password": "password123",
                "email": "test@test.com",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 400
        assert "at least 3 characters" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_register_admin_short_password(self, mock_get_col, client):
        """Test registration with too short password"""
        response = client.post(
            "/admin/register",
            params={
                "username": "testuser",
                "password": "12345",
                "email": "test@test.com",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 400
        assert "at least 6 characters" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_register_admin_invalid_email(self, mock_get_col, client):
        """Test registration with invalid email"""
        response = client.post(
            "/admin/register",
            params={
                "username": "testuser",
                "password": "password123",
                "email": "invalidemail",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 400
        assert "Invalid email" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_register_admin_short_full_name(self, mock_get_col, client):
        """Test registration with too short full name"""
        response = client.post(
            "/admin/register",
            params={
                "username": "testuser",
                "password": "password123",
                "email": "test@test.com",
                "full_name": "A"
            }
        )
        
        assert response.status_code == 400
        assert "Full name required" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_register_admin_db_not_configured(self, mock_get_col, client):
        """Test registration when database is not configured"""
        mock_get_col.return_value = None
        
        response = client.post(
            "/admin/register",
            params={
                "username": "testuser",
                "password": "password123",
                "email": "test@test.com",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 500
        assert "Database not configured" in response.json()["detail"]


# ============= ADMIN LOGIN TESTS =============


class TestAdminLogin:
    """Test admin login endpoint"""
    
    @patch("app.get_admin_collection")
    def test_login_success(self, mock_get_col, client, mock_db_collection, mock_admin):
        """Test successful login"""
        mock_db_collection.find_one.return_value = mock_admin
        mock_get_col.return_value = mock_db_collection
        
        response = client.post(
            "/admin/login",
            params={
                "username": "testadmin",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["admin"]["username"] == "testadmin"
    
    @patch("app.get_admin_collection")
    def test_login_user_not_found(self, mock_get_col, client, mock_db_collection):
        """Test login with non-existent user"""
        mock_db_collection.find_one.return_value = None
        mock_get_col.return_value = mock_db_collection
        
        response = client.post(
            "/admin/login",
            params={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_login_wrong_password(self, mock_get_col, client, mock_db_collection, mock_admin):
        """Test login with wrong password"""
        mock_db_collection.find_one.return_value = mock_admin
        mock_get_col.return_value = mock_db_collection
        
        response = client.post(
            "/admin/login",
            params={
                "username": "testadmin",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_login_inactive_account(self, mock_get_col, client, mock_db_collection, mock_admin):
        """Test login with inactive account"""
        mock_admin["is_active"] = False
        mock_db_collection.find_one.return_value = mock_admin
        mock_get_col.return_value = mock_db_collection
        
        response = client.post(
            "/admin/login",
            params={
                "username": "testadmin",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"]
    
    @patch("app.get_admin_collection")
    def test_login_db_not_configured(self, mock_get_col, client):
        """Test login when database is not configured"""
        mock_get_col.return_value = None
        
        response = client.post(
            "/admin/login",
            params={
                "username": "testadmin",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 500
        assert "Database not configured" in response.json()["detail"]


# ============= TOKEN VERIFICATION TESTS =============


class TestTokenVerification:
    """Test token verification endpoint"""
    
    def test_verify_token_success(self, client, valid_token):
        """Test successful token verification"""
        response = client.get(
            "/admin/verify-token",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "valid"
        assert "admin_id" in data
    
    def test_verify_token_missing_header(self, client):
        """Test verification without authorization header"""
        response = client.get("/admin/verify-token")
        
        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["detail"]
    
    def test_verify_token_invalid_format(self, client):
        """Test verification with invalid header format"""
        response = client.get(
            "/admin/verify-token",
            headers={"Authorization": "InvalidFormat"}
        )
        
        assert response.status_code == 401
        assert "Invalid authorization header format" in response.json()["detail"]
    
    def test_verify_token_wrong_scheme(self, client, valid_token):
        """Test verification with wrong authentication scheme"""
        response = client.get(
            "/admin/verify-token",
            headers={"Authorization": f"Basic {valid_token}"}
        )
        
        assert response.status_code == 401
        assert "Invalid authentication scheme" in response.json()["detail"]
    
    def test_verify_token_expired(self, client, expired_token):
        """Test verification with expired token"""
        response = client.get(
            "/admin/verify-token",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
        assert "Token expired" in response.json()["detail"]
    
    def test_verify_token_invalid(self, client):
        """Test verification with invalid token"""
        response = client.get(
            "/admin/verify-token",
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]


# ============= ADMIN UPLOAD TESTS =============


class TestAdminUpload:
    """Test admin file upload endpoint"""
    
    def test_upload_without_token(self, client, mock_file):
        """Test upload without authentication token"""
        response = client.post(
            "/admin/upload",
            files={"files": mock_file}
        )
        
        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["detail"]
    
    def test_upload_with_invalid_token(self, client, mock_file):
        """Test upload with invalid token"""
        response = client.post(
            "/admin/upload",
            files={"files": mock_file},
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


# ============= ADMIN STATS TESTS =============


class TestAdminStats:
    """Test admin statistics endpoint"""
    
    def test_stats_without_token(self, client):
        """Test stats without authentication"""
        response = client.get("/admin/stats")
        
        assert response.status_code == 401


# ============= ADMIN LOGOUT TESTS =============


class TestAdminLogout:
    """Test admin logout endpoint"""
    
    def test_logout_success(self, client, valid_token):
        """Test successful logout"""
        response = client.post(
            "/admin/logout",
            headers={"Authorization": f"Bearer {valid_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Logged out successfully" in data["message"]
    
    def test_logout_without_token(self, client):
        """Test logout without token"""
        response = client.post("/admin/logout")
        
        assert response.status_code == 401
    
    def test_logout_invalid_token(self, client):
        """Test logout with invalid token"""
        response = client.post(
            "/admin/logout",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


# ============= HEALTH CHECK TESTS =============


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "File Integrity Service"


# ============= CLEANUP FUNCTION TESTS =============


class TestCleanupFunction:
    """Test cleanup_files_folder function"""
    
    @patch("os.path.exists")
    @patch("os.listdir")
    @patch("os.path.isfile")
    @patch("os.remove")
    def test_cleanup_success(self, mock_remove, mock_isfile, mock_listdir, mock_exists):
        """Test successful cleanup"""
        from app import cleanup_files_folder
        
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt"]
        mock_isfile.return_value = True
        
        result = cleanup_files_folder()
        
        assert result is True
        assert mock_remove.call_count == 2
    
    @patch("os.path.exists")
    def test_cleanup_folder_not_exists(self, mock_exists):
        """Test cleanup when folder doesn't exist"""
        from app import cleanup_files_folder
        
        mock_exists.return_value = False
        
        result = cleanup_files_folder()
        
        assert result is False
    
    @patch("os.path.exists")
    @patch("os.listdir")
    def test_cleanup_error(self, mock_listdir, mock_exists):
        """Test cleanup with error"""
        from app import cleanup_files_folder
        
        mock_exists.return_value = True
        mock_listdir.side_effect = Exception("Permission denied")
        
        result = cleanup_files_folder()
        
        assert result is False


# ============= EDGE CASE TESTS =============


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @patch("app.get_admin_collection")
    def test_register_with_empty_strings(self, mock_get_col, client):
        """Test registration with empty string values"""
        response = client.post(
            "/admin/register",
            params={
                "username": "",
                "password": "",
                "email": "",
                "full_name": ""
            }
        )
        
        assert response.status_code == 400
    
    @patch("app.get_admin_collection")
    def test_register_with_special_characters(self, mock_get_col, client, mock_db_collection):
        """Test registration with special characters"""
        mock_db_collection.find_one.return_value = None
        mock_db_collection.insert_one.return_value = Mock(inserted_id=ObjectId())
        mock_get_col.return_value = mock_db_collection
        
        response = client.post(
            "/admin/register",
            params={
                "username": "test@user#123",
                "password": "P@ssw0rd!",
                "email": "test+special@example.com",
                "full_name": "Test O'Brien-Smith"
            }
        )
        
        assert response.status_code == 200
    
    def test_token_with_multiple_bearer_words(self, client, valid_token):
        """Test token verification with malformed header"""
        response = client.get(
            "/admin/verify-token",
            headers={"Authorization": f"Bearer Bearer {valid_token}"}
        )
        
        assert response.status_code == 401


# ============= CONCURRENT REQUEST SIMULATION =============


class TestConcurrency:
    """Test concurrent request handling"""
    
    @patch("app.get_admin_collection")
    def test_multiple_simultaneous_logins(self, mock_get_col, client, mock_db_collection, mock_admin):
        """Test multiple login requests"""
        mock_db_collection.find_one.return_value = mock_admin
        mock_get_col.return_value = mock_db_collection
        
        responses = []
        for _ in range(5):
            response = client.post(
                "/admin/login",
                params={
                    "username": "testadmin",
                    "password": "testpass123"
                }
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert "access_token" in response.json()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])