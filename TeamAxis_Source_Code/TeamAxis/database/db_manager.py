"""
Database manager for TeamAxis project management system.
Handles all database operations using SQLite.
"""

import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
from database.models import User, Project, Task, License, Risk

class DatabaseManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path='teamaxis.db'):
        """Initialize database manager."""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def init_database(self):
        """Initialize database with required tables."""
        self.connect()
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                start_date DATE,
                end_date DATE,
                status TEXT DEFAULT 'active',
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                assignee_id INTEGER,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                due_date DATE,
                progress INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id),
                FOREIGN KEY (assignee_id) REFERENCES users(user_id)
            )
        ''')
        
        # Licenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS licenses (
                license_id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_key TEXT UNIQUE NOT NULL,
                user_id INTEGER,
                issue_date DATE,
                expiry_date DATE,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Risks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risks (
                risk_id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                description TEXT NOT NULL,
                severity TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'open',
                mitigation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(project_id)
            )
        ''')
        
        self.conn.commit()
        
        # Create default admin user if not exists
        self.create_default_admin()
        
        self.close()
    
    def create_default_admin(self):
        """Create default admin user."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ?', ('admin',))
        if cursor.fetchone()[0] == 0:
            password_hash = self.hash_password('admin123')
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', password_hash, 'admin@teamaxis.com', 'admin'))
            self.conn.commit()
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    # User operations
    def authenticate_user(self, username, password):
        """Authenticate user with username and password."""
        self.connect()
        cursor = self.conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute('''
            SELECT * FROM users WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        row = cursor.fetchone()
        self.close()
        if row:
            return User(row['user_id'], row['username'], row['password_hash'], 
                       row['email'], row['role'])
        return None
    
    def create_user(self, username, password, email, role='user'):
        """Create a new user."""
        self.connect()
        cursor = self.conn.cursor()
        password_hash = self.hash_password(password)
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            ''', (username, password_hash, email, role))
            self.conn.commit()
            user_id = cursor.lastrowid
            self.close()
            return user_id
        except sqlite3.IntegrityError:
            self.close()
            return None
    
    def get_all_users(self):
        """Get all users."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users')
        rows = cursor.fetchall()
        self.close()
        return [User(row['user_id'], row['username'], row['password_hash'], 
                    row['email'], row['role']) for row in rows]
    
    # Project operations
    def create_project(self, name, description, start_date, end_date, status='active', progress=0):
        """Create a new project."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, description, start_date, end_date, status, progress)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, start_date, end_date, status, progress))
        self.conn.commit()
        project_id = cursor.lastrowid
        self.close()
        return project_id
    
    def get_all_projects(self):
        """Get all projects."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
        rows = cursor.fetchall()
        self.close()
        return [Project(row['project_id'], row['name'], row['description'], 
                       row['start_date'], row['end_date'], row['status'], row['progress']) 
                for row in rows]
    
    def update_project_progress(self, project_id, progress):
        """Update project progress."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE projects SET progress = ? WHERE project_id = ?
        ''', (progress, project_id))
        self.conn.commit()
        self.close()
    
    def delete_project(self, project_id):
        """Delete a project and all related tasks and risks."""
        self.connect()
        cursor = self.conn.cursor()
        try:
            # Delete related tasks first
            cursor.execute('DELETE FROM tasks WHERE project_id = ?', (project_id,))
            # Delete related risks
            cursor.execute('DELETE FROM risks WHERE project_id = ?', (project_id,))
            # Delete the project
            cursor.execute('DELETE FROM projects WHERE project_id = ?', (project_id,))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            self.conn.rollback()
            self.close()
            return False
    
    # Task operations
    def create_task(self, project_id, name, description, assignee_id, status='pending', 
                   priority='medium', due_date=None, progress=0):
        """Create a new task."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (project_id, name, description, assignee_id, status, priority, due_date, progress)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, name, description, assignee_id, status, priority, due_date, progress))
        self.conn.commit()
        task_id = cursor.lastrowid
        self.close()
        return task_id
    
    def task_exists_in_project(self, project_id, task_name, due_date=None, exclude_task_id=None):
        """Check if a task with the same name and due date already exists in a project.
        
        Args:
            project_id: The project ID to check
            task_name: The task name to check
            due_date: The due date to check (optional, can be None)
            exclude_task_id: Optional task ID to exclude from check (useful when editing)
        """
        self.connect()
        cursor = self.conn.cursor()
        
        # Handle NULL due_date comparison (both must be NULL or both must match)
        if due_date is None or due_date == '':
            # Check for tasks with NULL due_date
            if exclude_task_id:
                cursor.execute('''SELECT COUNT(*) FROM tasks 
                                 WHERE project_id = ? 
                                 AND LOWER(name) = LOWER(?) 
                                 AND (due_date IS NULL OR due_date = '')
                                 AND task_id != ?''', 
                              (project_id, task_name.strip(), exclude_task_id))
            else:
                cursor.execute('''SELECT COUNT(*) FROM tasks 
                                 WHERE project_id = ? 
                                 AND LOWER(name) = LOWER(?) 
                                 AND (due_date IS NULL OR due_date = '')''', 
                              (project_id, task_name.strip()))
        else:
            # Check for tasks with matching due_date
            if exclude_task_id:
                cursor.execute('''SELECT COUNT(*) FROM tasks 
                                 WHERE project_id = ? 
                                 AND LOWER(name) = LOWER(?) 
                                 AND due_date = ?
                                 AND task_id != ?''', 
                              (project_id, task_name.strip(), due_date.strip(), exclude_task_id))
            else:
                cursor.execute('''SELECT COUNT(*) FROM tasks 
                                 WHERE project_id = ? 
                                 AND LOWER(name) = LOWER(?) 
                                 AND due_date = ?''', 
                              (project_id, task_name.strip(), due_date.strip()))
        
        count = cursor.fetchone()[0]
        self.close()
        return count > 0
    
    def get_task_by_id(self, task_id):
        """Get a task by its ID."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        row = cursor.fetchone()
        self.close()
        if row:
            return Task(row['task_id'], row['project_id'], row['name'], row['description'],
                       row['assignee_id'], row['status'], row['priority'], row['due_date'], row['progress'])
        return None
    
    def get_tasks_by_project(self, project_id):
        """Get all tasks for a project."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,))
        rows = cursor.fetchall()
        self.close()
        return [Task(row['task_id'], row['project_id'], row['name'], row['description'],
                    row['assignee_id'], row['status'], row['priority'], row['due_date'], row['progress'])
                for row in rows]
    
    def get_all_tasks(self):
        """Get all tasks."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        rows = cursor.fetchall()
        self.close()
        return [Task(row['task_id'], row['project_id'], row['name'], row['description'],
                    row['assignee_id'], row['status'], row['priority'], row['due_date'], row['progress'])
                for row in rows]
    
    def update_task_status(self, task_id, status, progress=None):
        """Update task status and progress."""
        self.connect()
        cursor = self.conn.cursor()
        if progress is not None:
            cursor.execute('''
                UPDATE tasks SET status = ?, progress = ? WHERE task_id = ?
            ''', (status, progress, task_id))
        else:
            cursor.execute('''
                UPDATE tasks SET status = ? WHERE task_id = ?
            ''', (status, task_id))
        self.conn.commit()
        self.close()
    
    def update_task(self, task_id, name, description, assignee_id, status, priority, due_date, progress=None):
        """Update task details."""
        self.connect()
        cursor = self.conn.cursor()
        if progress is not None:
            cursor.execute('''
                UPDATE tasks SET name = ?, description = ?, assignee_id = ?, status = ?, 
                priority = ?, due_date = ?, progress = ? WHERE task_id = ?
            ''', (name, description, assignee_id, status, priority, due_date, progress, task_id))
        else:
            cursor.execute('''
                UPDATE tasks SET name = ?, description = ?, assignee_id = ?, status = ?, 
                priority = ?, due_date = ? WHERE task_id = ?
            ''', (name, description, assignee_id, status, priority, due_date, task_id))
        self.conn.commit()
        self.close()
        return True
    
    def delete_task(self, task_id):
        """Delete a task."""
        self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM tasks WHERE task_id = ?', (task_id,))
            self.conn.commit()
            self.close()
            return True
        except Exception as e:
            self.conn.rollback()
            self.close()
            return False
    
    # License operations
    def create_license(self, license_key, user_id, issue_date, expiry_date, status='active'):
        """Create a new license."""
        self.connect()
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO licenses (license_key, user_id, issue_date, expiry_date, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (license_key, user_id, issue_date, expiry_date, status))
            self.conn.commit()
            license_id = cursor.lastrowid
            self.close()
            return license_id
        except sqlite3.IntegrityError:
            self.close()
            return None
    
    def get_all_licenses(self):
        """Get all licenses."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM licenses')
        rows = cursor.fetchall()
        self.close()
        return [License(row['license_id'], row['license_key'], row['user_id'],
                       row['issue_date'], row['expiry_date'], row['status']) for row in rows]
    
    def update_license_status(self, license_id, status):
        """Update license status."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('UPDATE licenses SET status = ? WHERE license_id = ?', (status, license_id))
        self.conn.commit()
        self.close()
    
    def assign_license_to_user(self, license_id, user_id):
        """Assign a license to a user."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('UPDATE licenses SET user_id = ? WHERE license_id = ?', (user_id, license_id))
        self.conn.commit()
        self.close()
    
    # Risk operations
    def create_risk(self, project_id, description, severity='medium', status='open', mitigation=None):
        """Create a new risk."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO risks (project_id, description, severity, status, mitigation)
            VALUES (?, ?, ?, ?, ?)
        ''', (project_id, description, severity, status, mitigation))
        self.conn.commit()
        risk_id = cursor.lastrowid
        self.close()
        return risk_id
    
    def get_risks_by_project(self, project_id):
        """Get all risks for a project."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM risks WHERE project_id = ?', (project_id,))
        rows = cursor.fetchall()
        self.close()
        return [Risk(row['risk_id'], row['project_id'], row['description'],
                    row['severity'], row['status'], row['mitigation']) for row in rows]
    
    def get_all_risks(self):
        """Get all risks."""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM risks')
        rows = cursor.fetchall()
        self.close()
        return [Risk(row['risk_id'], row['project_id'], row['description'],
                    row['severity'], row['status'], row['mitigation']) for row in rows]
    
    def update_risk_status(self, risk_id, status, mitigation=None):
        """Update risk status and mitigation."""
        self.connect()
        cursor = self.conn.cursor()
        if mitigation:
            cursor.execute('''
                UPDATE risks SET status = ?, mitigation = ? WHERE risk_id = ?
            ''', (status, mitigation, risk_id))
        else:
            cursor.execute('UPDATE risks SET status = ? WHERE risk_id = ?', (status, risk_id))
        self.conn.commit()
        self.close()

