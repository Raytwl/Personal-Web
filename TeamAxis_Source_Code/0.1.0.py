import sqlite3
import hashlib
import os
import binascii
import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import time

# Utility functions
def get_current_datetime():
    return datetime.datetime.now().isoformat()

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

def generate_salt():
    return os.urandom(16)

def generate_machine_fingerprint():
    # Simplified fingerprint (in real app, use hardware IDs)
    return hashlib.sha256(os.urandom(32)).hexdigest()

# Database connection (singleton-like)
class DatabaseConnection:
    _connection = None

    @classmethod
    def get_connection(cls, db_path='teamaxis.db'):
        if cls._connection is None:
            cls._connection = sqlite3.connect(db_path, check_same_thread=False)
            cls._connection.execute('PRAGMA foreign_keys = ON;')
            cls._connection.execute('PRAGMA journal_mode = WAL;')
        return cls._connection

# Schema creation
def create_schema():
    conn = DatabaseConnection.get_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash BLOB NOT NULL,
        salt BLOB NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        last_login TEXT
    );
    ''')
    
    # Licenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS licenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT NOT NULL UNIQUE,
        activation_date TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        is_valid INTEGER DEFAULT 1,
        machine_fingerprint TEXT
    );
    ''')
    
    # Projects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        created_by INTEGER REFERENCES users(id),
        created_at TEXT DEFAULT (datetime('now')),
        risk_score REAL DEFAULT 0
    );
    ''')
    
    # Team members table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        name TEXT NOT NULL,
        role TEXT,
        department TEXT,
        max_workload INTEGER DEFAULT 40
    );
    ''')
    
    # Skills table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS team_member_skills (
        team_member_id INTEGER REFERENCES team_members(id),
        skill_id INTEGER REFERENCES skills(id),
        proficiency_level INTEGER CHECK(proficiency_level BETWEEN 1 AND 5),
        PRIMARY KEY (team_member_id, skill_id)
    );
    ''')
    
    # Tasks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER REFERENCES projects(id),
        title TEXT NOT NULL,
        description TEXT,
        assignee_id INTEGER REFERENCES team_members(id),
        start_date TEXT,
        due_date TEXT NOT NULL,
        status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'blocked')) DEFAULT 'pending',
        estimated_hours REAL,
        actual_hours REAL DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS task_skills (
        task_id INTEGER REFERENCES tasks(id),
        skill_id INTEGER REFERENCES skills(id),
        required_level INTEGER CHECK(required_level BETWEEN 1 AND 5),
        PRIMARY KEY (task_id, skill_id)
    );
    ''')
    
    # Task history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS task_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER REFERENCES tasks(id),
        changed_by INTEGER REFERENCES users(id),
        changed_at TEXT DEFAULT (datetime('now')),
        field_name TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT
    );
    ''')
    
    # Backups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backup_path TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        backup_type TEXT CHECK(backup_type IN ('manual', 'automatic')),
        description TEXT
    );
    ''')
    
    # Indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_assignee ON tasks(assignee_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_team_member_skills ON team_member_skills(team_member_id);')
    
    conn.commit()

# Repository base class
class Repository:
    def __init__(self, table_name):
        self.table_name = table_name
        self.conn = DatabaseConnection.get_connection()
    
    def execute_transaction(self, operation):
        cursor = self.conn.cursor()
        try:
            cursor.execute('BEGIN TRANSACTION;')
            result = operation(cursor)
            cursor.execute('COMMIT;')
            return result
        except Exception as e:
            cursor.execute('ROLLBACK;')
            raise e

# Example repositories (simplified)
class UserRepository(Repository):
    def __init__(self):
        super().__init__('users')
    
    def save(self, username, password):
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        def op(cursor):
            cursor.execute('INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)',
                           (username, password_hash, salt))
            return cursor.lastrowid
        return self.execute_transaction(op)
    
    def find_by_username(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'username': row[1], 'password_hash': row[2], 'salt': row[3]}
        return None
    
    def validate_password(self, user, password):
        return hash_password(password, user['salt']) == user['password_hash']

class LicenseRepository(Repository):
    def __init__(self):
        super().__init__('licenses')
    
    def find_by_key(self, key):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM licenses WHERE license_key = ?', (key,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'license_key': row[1], 'activation_date': row[2], 'expiry_date': row[3],
                    'is_valid': bool(row[4]), 'machine_fingerprint': row[5]}
        return {'id': 0}
    
    def save(self, license):
        def op(cursor):
            cursor.execute('''
            INSERT INTO licenses (license_key, activation_date, expiry_date, is_valid, machine_fingerprint)
            VALUES (?, ?, ?, ?, ?)
            ''', (license['license_key'], license['activation_date'], license['expiry_date'],
                  int(license['is_valid']), license['machine_fingerprint']))
        self.execute_transaction(op)
    
    def update(self, license):
        def op(cursor):
            cursor.execute('''
            UPDATE licenses SET is_valid = ? WHERE license_key = ?
            ''', (int(license['is_valid']), license['license_key']))
        self.execute_transaction(op)

# License Controller
class LicenseController:
    def __init__(self):
        self.repo = LicenseRepository()
    
    def validate_license(self, license_key):
        import re
        if not re.match(r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$', license_key):
            return False
        
        machine_fingerprint = generate_machine_fingerprint()
        license = self.repo.find_by_key(license_key)
        
        if license['id'] == 0:
            # Simulate internal validation (in real, use proper algo)
            if self.internal_validation_algorithm(license_key, machine_fingerprint):
                activation = get_current_datetime()
                expiry = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
                new_license = {'license_key': license_key, 'activation_date': activation, 'expiry_date': expiry,
                               'is_valid': True, 'machine_fingerprint': machine_fingerprint}
                self.repo.save(new_license)
                return True
            return False
        
        is_not_expired = datetime.datetime.now().isoformat() < license['expiry_date']
        is_machine_match = machine_fingerprint == license['machine_fingerprint']
        is_valid = license['is_valid'] and is_not_expired and is_machine_match
        
        if not is_valid:
            license['is_valid'] = False
            self.repo.update(license)
        
        return is_valid
    
    def internal_validation_algorithm(self, key, fingerprint):
        # Placeholder - in real app, implement proper validation
        return True  # For demo

# Backup Manager
class BackupManager:
    def create_backup(self, backup_path, backup_type='manual'):
        conn = DatabaseConnection.get_connection()
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            backup_conn = sqlite3.connect(backup_path)
            query = ''.join(line for line in conn.iterdump())
            backup_conn.executescript(query)
            backup_conn.close()
            
            # Record metadata
            repo = Repository('backups')
            def op(cursor):
                cursor.execute('INSERT INTO backups (backup_path, backup_type) VALUES (?, ?)',
                               (backup_path, backup_type))
            repo.execute_transaction(op)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False

# Risk Calculator (simplified)
class RiskCalculator:
    def calculate_project_risk(self, project_id):
        # Placeholder calculations
        schedule_deviation = 20.0  # Example
        resource_utilization = 50.0  # Example
        risk_score = 0.6 * schedule_deviation + 0.4 * resource_utilization
        # Update project (omitted for brevity)
        return risk_score

# UI Components (Tkinter)
class TeamAxisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TeamAxis")
        self.user_repo = UserRepository()
        self.license_controller = LicenseController()
        self.is_licensed = False
        self.current_user = None
        self.show_login()
    
    def show_login(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()
        
        ttk.Label(frame, text="Username:").grid(row=0, column=0)
        username_entry = ttk.Entry(frame)
        username_entry.grid(row=0, column=1)
        
        ttk.Label(frame, text="Password:").grid(row=1, column=0)
        password_entry = ttk.Entry(frame, show="*")
        password_entry.grid(row=1, column=1)
        
        ttk.Button(frame, text="Login", command=lambda: self.login(username_entry.get(), password_entry.get())).grid(row=2, column=0)
        ttk.Button(frame, text="Register", command=lambda: self.register(username_entry.get(), password_entry.get())).grid(row=2, column=1)
    
    def login(self, username, password):
        user = self.user_repo.find_by_username(username)
        if user and self.user_repo.validate_password(user, password):
            self.current_user = user
            self.show_license_check()
        else:
            messagebox.showerror("Error", "Invalid credentials")
    
    def register(self, username, password):
        try:
            self.user_repo.save(username, password)
            messagebox.showinfo("Success", "Registered successfully")
        except:
            messagebox.showerror("Error", "Username exists")
    
    def show_license_check(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()
        
        ttk.Label(frame, text="License Key:").grid(row=0, column=0)
        key_entry = ttk.Entry(frame)
        key_entry.grid(row=0, column=1)
        
        ttk.Button(frame, text="Validate", command=lambda: self.validate_and_proceed(key_entry.get())).grid(row=1, column=0)
    
    def validate_and_proceed(self, key):
        if self.license_controller.validate_license(key):
            self.is_licensed = True
            messagebox.showinfo("Success", "License valid")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid license")
    
    def show_dashboard(self):
        # Placeholder for dashboard
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()
        ttk.Label(frame, text="Welcome to TeamAxis Dashboard").grid()
        # Add more UI elements for projects, tasks, etc.
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    create_schema()
    app = TeamAxisApp()
    app.run()