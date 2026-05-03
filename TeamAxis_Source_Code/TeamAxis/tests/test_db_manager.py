"""
Tests for database/db_manager.py
"""

import pytest
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from database.models import User, Project, Task, License, Risk

class TestDatabaseManager:
    """Test DatabaseManager class."""
    
    def test_init_database(self, temp_db):
        """Test database initialization."""
        assert temp_db.conn is not None
        temp_db.close()
        assert temp_db.conn is None
    
    def test_hash_password(self):
        """Test password hashing."""
        password = "testpassword"
        hash1 = DatabaseManager.hash_password(password)
        hash2 = DatabaseManager.hash_password(password)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64 char hex string
        assert hash1 != password
    
    def test_create_user(self, temp_db):
        """Test user creation."""
        user_id = temp_db.create_user('newuser', 'password123', 'user@test.com', 'user')
        assert user_id is not None
        assert isinstance(user_id, int)
        
        # Test duplicate username
        user_id2 = temp_db.create_user('newuser', 'password456', 'user2@test.com', 'user')
        assert user_id2 is None
    
    def test_authenticate_user(self, temp_db):
        """Test user authentication."""
        # Create user
        user_id = temp_db.create_user('authuser', 'authpass', 'auth@test.com', 'user')
        
        # Test successful authentication
        user = temp_db.authenticate_user('authuser', 'authpass')
        assert user is not None
        assert user.username == 'authuser'
        assert user.email == 'auth@test.com'
        
        # Test failed authentication
        user = temp_db.authenticate_user('authuser', 'wrongpass')
        assert user is None
        
        user = temp_db.authenticate_user('nonexistent', 'password')
        assert user is None
    
    def test_get_all_users(self, temp_db):
        """Test getting all users."""
        # Initially should have admin user
        users = temp_db.get_all_users()
        initial_count = len(users)
        
        # Create additional users
        temp_db.create_user('user1', 'pass1', 'user1@test.com', 'user')
        temp_db.create_user('user2', 'pass2', 'user2@test.com', 'user')
        
        users = temp_db.get_all_users()
        assert len(users) == initial_count + 2
    
    def test_create_project(self, temp_db):
        """Test project creation."""
        project_id = temp_db.create_project(
            'New Project',
            'Project Description',
            '2024-01-01',
            '2024-12-31',
            'active',
            50
        )
        assert project_id is not None
        assert isinstance(project_id, int)
    
    def test_get_all_projects(self, temp_db):
        """Test getting all projects."""
        # Create multiple projects
        temp_db.create_project('Project 1', 'Desc 1', '2024-01-01', '2024-12-31')
        temp_db.create_project('Project 2', 'Desc 2', '2024-02-01', '2024-12-31')
        
        projects = temp_db.get_all_projects()
        assert len(projects) >= 2
        assert all(isinstance(p, Project) for p in projects)
    
    def test_update_project_progress(self, temp_db, sample_project):
        """Test updating project progress."""
        temp_db.update_project_progress(sample_project.project_id, 75)
        
        projects = temp_db.get_all_projects()
        updated_project = next(p for p in projects if p.project_id == sample_project.project_id)
        assert updated_project.progress == 75
    
    def test_delete_project(self, temp_db, sample_project):
        """Test project deletion."""
        project_id = sample_project.project_id
        
        # Create tasks and risks for the project
        task_id = temp_db.create_task(project_id, 'Task 1', 'Desc', None, 'pending')
        risk_id = temp_db.create_risk(project_id, 'Risk 1', 'high')
        
        # Delete project
        result = temp_db.delete_project(project_id)
        assert result is True
        
        # Verify project is deleted
        projects = temp_db.get_all_projects()
        assert not any(p.project_id == project_id for p in projects)
        
        # Verify related tasks are deleted
        tasks = temp_db.get_all_tasks()
        assert not any(t.task_id == task_id for t in tasks)
        
        # Verify related risks are deleted
        risks = temp_db.get_all_risks()
        assert not any(r.risk_id == risk_id for r in risks)
    
    def test_create_task(self, temp_db, sample_project, sample_user):
        """Test task creation."""
        task_id = temp_db.create_task(
            sample_project.project_id,
            'New Task',
            'Task Description',
            sample_user.user_id,
            'pending',
            'high',
            '2024-06-01',
            0
        )
        assert task_id is not None
        assert isinstance(task_id, int)
    
    def test_task_exists_in_project(self, temp_db, sample_project):
        """Test duplicate task detection."""
        task_name = 'Duplicate Task'
        due_date = '2024-06-01'
        
        # Create first task
        temp_db.create_task(sample_project.project_id, task_name, 'Desc', None, 'pending', 'medium', due_date)
        
        # Check if duplicate exists
        exists = temp_db.task_exists_in_project(sample_project.project_id, task_name, due_date)
        assert exists is True
        
        # Check with different due date
        exists = temp_db.task_exists_in_project(sample_project.project_id, task_name, '2024-07-01')
        assert exists is False
        
        # Check with None due date
        temp_db.create_task(sample_project.project_id, 'No Date Task', 'Desc', None, 'pending', 'medium', None)
        exists = temp_db.task_exists_in_project(sample_project.project_id, 'No Date Task', None)
        assert exists is True
    
    def test_task_exists_exclude_task_id(self, temp_db, sample_project):
        """Test duplicate task detection with exclusion."""
        task_name = 'Edit Task'
        due_date = '2024-06-01'
        
        # Create task
        task_id = temp_db.create_task(sample_project.project_id, task_name, 'Desc', None, 'pending', 'medium', due_date)
        
        # Should not detect itself as duplicate
        exists = temp_db.task_exists_in_project(sample_project.project_id, task_name, due_date, exclude_task_id=task_id)
        assert exists is False
        
        # Should detect other task with same name and date
        task_id2 = temp_db.create_task(sample_project.project_id, 'Other Task', 'Desc', None, 'pending', 'medium', due_date)
        exists = temp_db.task_exists_in_project(sample_project.project_id, task_name, due_date, exclude_task_id=task_id2)
        assert exists is True
    
    def test_get_task_by_id(self, temp_db, sample_task):
        """Test getting task by ID."""
        task = temp_db.get_task_by_id(sample_task.task_id)
        assert task is not None
        assert task.task_id == sample_task.task_id
        assert task.name == sample_task.name
        
        # Test non-existent task
        task = temp_db.get_task_by_id(99999)
        assert task is None
    
    def test_get_tasks_by_project(self, temp_db, sample_project, sample_user):
        """Test getting tasks by project."""
        # Create multiple tasks
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending')
        temp_db.create_task(sample_project.project_id, 'Task 2', 'Desc', sample_user.user_id, 'in_progress')
        
        tasks = temp_db.get_tasks_by_project(sample_project.project_id)
        assert len(tasks) >= 2
        assert all(t.project_id == sample_project.project_id for t in tasks)
    
    def test_get_all_tasks(self, temp_db, sample_project, sample_user):
        """Test getting all tasks."""
        # Create tasks
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending')
        temp_db.create_task(sample_project.project_id, 'Task 2', 'Desc', sample_user.user_id, 'completed')
        
        tasks = temp_db.get_all_tasks()
        assert len(tasks) >= 2
        assert all(isinstance(t, Task) for t in tasks)
    
    def test_update_task_status(self, temp_db, sample_task):
        """Test updating task status."""
        temp_db.update_task_status(sample_task.task_id, 'completed', 100)
        
        updated_task = temp_db.get_task_by_id(sample_task.task_id)
        assert updated_task.status == 'completed'
        assert updated_task.progress == 100
    
    def test_update_task(self, temp_db, sample_task, sample_user):
        """Test updating task details."""
        temp_db.update_task(
            sample_task.task_id,
            'Updated Task Name',
            'Updated Description',
            sample_user.user_id,
            'in_progress',
            'high',
            '2024-07-01',
            50
        )
        
        updated_task = temp_db.get_task_by_id(sample_task.task_id)
        assert updated_task.name == 'Updated Task Name'
        assert updated_task.description == 'Updated Description'
        assert updated_task.status == 'in_progress'
        assert updated_task.priority == 'high'
        assert updated_task.progress == 50
    
    def test_delete_task(self, temp_db, sample_task):
        """Test task deletion."""
        task_id = sample_task.task_id
        result = temp_db.delete_task(task_id)
        assert result is True
        
        task = temp_db.get_task_by_id(task_id)
        assert task is None
    
    def test_create_license(self, temp_db, sample_user):
        """Test license creation."""
        license_id = temp_db.create_license(
            'TEST-1234-5678-9012',
            sample_user.user_id,
            '2024-01-01',
            '2025-01-01',
            'active'
        )
        assert license_id is not None
        assert isinstance(license_id, int)
        
        # Test duplicate license key
        license_id2 = temp_db.create_license(
            'TEST-1234-5678-9012',
            sample_user.user_id,
            '2024-01-01',
            '2025-01-01',
            'active'
        )
        assert license_id2 is None
    
    def test_get_all_licenses(self, temp_db, sample_user):
        """Test getting all licenses."""
        temp_db.create_license('KEY1-1111-2222-3333', sample_user.user_id, '2024-01-01', '2025-01-01')
        temp_db.create_license('KEY2-4444-5555-6666', None, '2024-01-01', '2025-01-01')
        
        licenses = temp_db.get_all_licenses()
        assert len(licenses) >= 2
        assert all(isinstance(l, License) for l in licenses)
    
    def test_update_license_status(self, temp_db, sample_user):
        """Test updating license status."""
        license_id = temp_db.create_license(
            'STATUS-TEST-KEY-1234',
            sample_user.user_id,
            '2024-01-01',
            '2025-01-01',
            'active'
        )
        
        temp_db.update_license_status(license_id, 'revoked')
        
        licenses = temp_db.get_all_licenses()
        updated_license = next(l for l in licenses if l.license_id == license_id)
        assert updated_license.status == 'revoked'
    
    def test_assign_license_to_user(self, temp_db, sample_user):
        """Test assigning license to user."""
        license_id = temp_db.create_license(
            'ASSIGN-TEST-KEY-1234',
            None,
            '2024-01-01',
            '2025-01-01',
            'active'
        )
        
        temp_db.assign_license_to_user(license_id, sample_user.user_id)
        
        licenses = temp_db.get_all_licenses()
        updated_license = next(l for l in licenses if l.license_id == license_id)
        assert updated_license.user_id == sample_user.user_id
    
    def test_create_risk(self, temp_db, sample_project):
        """Test risk creation."""
        risk_id = temp_db.create_risk(
            sample_project.project_id,
            'Test Risk',
            'high',
            'open',
            'Mitigation plan'
        )
        assert risk_id is not None
        assert isinstance(risk_id, int)
    
    def test_get_risks_by_project(self, temp_db, sample_project):
        """Test getting risks by project."""
        temp_db.create_risk(sample_project.project_id, 'Risk 1', 'high')
        temp_db.create_risk(sample_project.project_id, 'Risk 2', 'medium')
        
        risks = temp_db.get_risks_by_project(sample_project.project_id)
        assert len(risks) >= 2
        assert all(r.project_id == sample_project.project_id for r in risks)
    
    def test_get_all_risks(self, temp_db, sample_project):
        """Test getting all risks."""
        temp_db.create_risk(sample_project.project_id, 'Risk 1', 'high')
        temp_db.create_risk(sample_project.project_id, 'Risk 2', 'low')
        
        risks = temp_db.get_all_risks()
        assert len(risks) >= 2
        assert all(isinstance(r, Risk) for r in risks)
    
    def test_update_risk_status(self, temp_db, sample_project):
        """Test updating risk status."""
        risk_id = temp_db.create_risk(sample_project.project_id, 'Test Risk', 'high', 'open')
        
        temp_db.update_risk_status(risk_id, 'mitigated', 'Risk has been mitigated')
        
        risks = temp_db.get_all_risks()
        updated_risk = next(r for r in risks if r.risk_id == risk_id)
        assert updated_risk.status == 'mitigated'
        assert updated_risk.mitigation == 'Risk has been mitigated'

