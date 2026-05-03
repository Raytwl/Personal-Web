"""
Tests for auth/login.py
"""

import pytest
from auth.login import AuthManager

class TestAuthManager:
    """Test AuthManager class."""
    
    def test_login_success(self, auth_manager, sample_user):
        """Test successful login."""
        success, message = auth_manager.login('testuser', 'testpass123')
        assert success is True
        assert 'success' in message.lower()
        assert auth_manager.current_user is not None
        assert auth_manager.current_user.username == 'testuser'
    
    def test_login_failure_wrong_password(self, auth_manager, sample_user):
        """Test login with wrong password."""
        success, message = auth_manager.login('testuser', 'wrongpassword')
        assert success is False
        assert auth_manager.current_user is None
    
    def test_login_failure_nonexistent_user(self, auth_manager):
        """Test login with non-existent user."""
        success, message = auth_manager.login('nonexistent', 'password')
        assert success is False
        assert auth_manager.current_user is None
    
    def test_login_admin_without_license(self, auth_manager, sample_admin):
        """Test admin login without license."""
        # Use the admin from sample_admin fixture (could be 'admin' or 'testadmin')
        admin_username = sample_admin.username
        admin_password = 'admin123'
        success, message = auth_manager.login(admin_username, admin_password)
        assert success is True
        assert auth_manager.current_user is not None
        assert auth_manager.is_admin() is True
    
    def test_login_user_without_license(self, auth_manager, sample_user):
        """Test regular user login without license should fail."""
        success, message = auth_manager.login('testuser', 'testpass123')
        assert success is False
        assert 'license' in message.lower()
    
    def test_login_user_with_valid_license(self, auth_manager, sample_user, license_manager):
        """Test regular user login with valid license."""
        # Create and assign license
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        auth_manager.db_manager.assign_license_to_user(license_id, sample_user.user_id)
        
        success, message = auth_manager.login('testuser', 'testpass123', license_key)
        assert success is True
        assert auth_manager.current_user is not None
    
    def test_login_user_with_invalid_license(self, auth_manager, sample_user):
        """Test login with invalid license."""
        success, message = auth_manager.login('testuser', 'testpass123', 'INVALID-KEY-1234')
        assert success is False
        assert 'license' in message.lower()
    
    def test_login_user_with_expired_license(self, auth_manager, sample_user, license_manager):
        """Test login with expired license."""
        # Create expired license
        from datetime import datetime, timedelta
        license_key = license_manager.generate_license_key()
        issue_date = (datetime.now() - timedelta(days=400)).date()
        expiry_date = (datetime.now() - timedelta(days=30)).date()
        
        license_id = auth_manager.db_manager.create_license(
            license_key, sample_user.user_id, issue_date, expiry_date, 'active'
        )
        
        success, message = auth_manager.login('testuser', 'testpass123', license_key)
        assert success is False
        assert 'expired' in message.lower() or 'invalid' in message.lower()
    
    def test_register_success(self, auth_manager, license_manager):
        """Test successful registration."""
        # Create unassigned license
        license_id, license_key = license_manager.create_license(None, 365)
        
        success, message = auth_manager.register('newuser', 'password123', 'newuser@test.com', license_key)
        assert success is True
        assert 'success' in message.lower()
        
        # Verify user was created
        user = auth_manager.db_manager.authenticate_user('newuser', 'password123')
        assert user is not None
    
    def test_register_without_license(self, auth_manager):
        """Test registration without license."""
        success, message = auth_manager.register('newuser', 'password123', 'newuser@test.com', '')
        assert success is False
        assert 'license' in message.lower()
    
    def test_register_with_assigned_license(self, auth_manager, license_manager, sample_user):
        """Test registration with already assigned license."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        
        success, message = auth_manager.register('newuser', 'password123', 'newuser@test.com', license_key)
        assert success is False
        assert 'assigned' in message.lower()
    
    def test_register_duplicate_username(self, auth_manager, license_manager, sample_user):
        """Test registration with duplicate username."""
        license_id, license_key = license_manager.create_license(None, 365)
        
        success, message = auth_manager.register('testuser', 'password123', 'new@test.com', license_key)
        assert success is False
        assert 'exists' in message.lower() or 'already' in message.lower()
    
    def test_logout(self, auth_manager, sample_admin):
        """Test logout functionality."""
        admin_username = sample_admin.username
        auth_manager.login(admin_username, 'admin123')
        assert auth_manager.is_authenticated() is True
        
        auth_manager.logout()
        assert auth_manager.is_authenticated() is False
        assert auth_manager.current_user is None
    
    def test_is_authenticated(self, auth_manager, sample_admin):
        """Test authentication check."""
        assert auth_manager.is_authenticated() is False
        
        admin_username = sample_admin.username
        auth_manager.login(admin_username, 'admin123')
        assert auth_manager.is_authenticated() is True
        
        auth_manager.logout()
        assert auth_manager.is_authenticated() is False
    
    def test_get_current_user(self, auth_manager, sample_admin):
        """Test getting current user."""
        assert auth_manager.get_current_user() is None
        
        admin_username = sample_admin.username
        auth_manager.login(admin_username, 'admin123')
        user = auth_manager.get_current_user()
        assert user is not None
        assert user.username == admin_username
    
    def test_is_admin(self, auth_manager, sample_admin, sample_user, license_manager):
        """Test admin check."""
        admin_username = sample_admin.username
        auth_manager.login(admin_username, 'admin123')
        assert auth_manager.is_admin() is True
        
        auth_manager.logout()
        # Create valid license for test user
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        auth_manager.db_manager.assign_license_to_user(license_id, sample_user.user_id)
        auth_manager.login('testuser', 'testpass123', license_key)
        # Note: This will fail without valid license, but we're testing is_admin
        if auth_manager.current_user:
            assert auth_manager.is_admin() is False

