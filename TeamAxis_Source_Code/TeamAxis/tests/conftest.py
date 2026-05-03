"""
Pytest configuration and fixtures for TeamAxis tests.
"""

import pytest
import os
import tempfile
import shutil
from database.db_manager import DatabaseManager
from auth.login import AuthManager
from license.license_manager import LicenseManager

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_teamaxis.db')
    
    # Create database manager with temporary path
    db_manager = DatabaseManager(db_path)
    
    yield db_manager
    
    # Cleanup
    db_manager.close()
    if os.path.exists(db_path):
        os.remove(db_path)
    shutil.rmtree(temp_dir)

@pytest.fixture
def auth_manager(temp_db):
    """Create an AuthManager with temporary database."""
    # Replace the db_manager in auth_manager
    auth = AuthManager()
    auth.db_manager = temp_db
    auth.license_manager.db_manager = temp_db
    return auth

@pytest.fixture
def license_manager(temp_db):
    """Create a LicenseManager with temporary database."""
    license_mgr = LicenseManager()
    license_mgr.db_manager = temp_db
    return license_mgr

@pytest.fixture
def sample_user(temp_db):
    """Create a sample user for testing."""
    user_id = temp_db.create_user('testuser', 'testpass123', 'test@example.com', 'user')
    return temp_db.authenticate_user('testuser', 'testpass123')

@pytest.fixture
def sample_admin(temp_db):
    """Create a sample admin user for testing."""
    # Check if admin already exists (from default admin creation)
    existing_admin = temp_db.authenticate_user('admin', 'admin123')
    if existing_admin:
        return existing_admin
    # Otherwise create one
    user_id = temp_db.create_user('testadmin', 'admin123', 'admin@example.com', 'admin')
    return temp_db.authenticate_user('testadmin', 'admin123')

@pytest.fixture
def sample_project(temp_db):
    """Create a sample project for testing."""
    project_id = temp_db.create_project(
        'Test Project',
        'Test Description',
        '2024-01-01',
        '2024-12-31',
        'active',
        0
    )
    projects = temp_db.get_all_projects()
    return next(p for p in projects if p.project_id == project_id)

@pytest.fixture
def sample_task(temp_db, sample_project, sample_user):
    """Create a sample task for testing."""
    task_id = temp_db.create_task(
        sample_project.project_id,
        'Test Task',
        'Test Task Description',
        sample_user.user_id,
        'pending',
        'medium',
        '2024-06-01',
        0
    )
    return temp_db.get_task_by_id(task_id)

