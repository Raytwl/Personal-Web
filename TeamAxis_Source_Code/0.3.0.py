import sqlite3
import hashlib
import os
import binascii
import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import time
import re

# Utility functions
def get_current_datetime():
    return datetime.datetime.now().isoformat()

def parse_date(date_str):
    if date_str:
        return datetime.datetime.fromisoformat(date_str)
    return None

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

# User Repository
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
            return {'id': row[0], 'username': row[1], 'password_hash': row[2], 'salt': row[3],
                    'created_at': row[4], 'last_login': row[5]}
        return None
    
    def update_last_login(self, user_id):
        def op(cursor):
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?',
                           (get_current_datetime(), user_id))
        self.execute_transaction(op)
    
    def validate_password(self, user, password):
        return hash_password(password, user['salt']) == user['password_hash']

# License Repository
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

# Project Repository
class ProjectRepository(Repository):
    def __init__(self):
        super().__init__('projects')
    
    def save(self, project):
        def op(cursor):
            cursor.execute('''
            INSERT INTO projects (name, description, start_date, end_date, created_by)
            VALUES (?, ?, ?, ?, ?)
            ''', (project['name'], project['description'], project['start_date'],
                  project['end_date'], project['created_by']))
            return cursor.lastrowid
        return self.execute_transaction(op)
    
    def find_by_id(self, project_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'description': row[2], 'start_date': row[3],
                    'end_date': row[4], 'created_by': row[5], 'created_at': row[6], 'risk_score': row[7]}
        return None
    
    def find_all_by_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE created_by = ?', (user_id,))
        rows = cursor.fetchall()
        return [{'id': row[0], 'name': row[1], 'description': row[2], 'start_date': row[3],
                 'end_date': row[4], 'created_by': row[5], 'created_at': row[6], 'risk_score': row[7]} for row in rows]
    
    def update(self, project):
        def op(cursor):
            cursor.execute('''
            UPDATE projects SET name = ?, description = ?, start_date = ?, end_date = ?, risk_score = ?
            WHERE id = ?
            ''', (project['name'], project['description'], project['start_date'], project['end_date'],
                  project['risk_score'], project['id']))
        self.execute_transaction(op)
    
    def delete(self, project_id):
        def op(cursor):
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        self.execute_transaction(op)

# Task Repository
class TaskRepository(Repository):
    def __init__(self):
        super().__init__('tasks')
    
    def save(self, task):
        def op(cursor):
            cursor.execute('''
            INSERT INTO tasks (project_id, title, description, assignee_id, start_date, due_date, 
                               status, estimated_hours, actual_hours)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (task['project_id'], task['title'], task['description'], task['assignee_id'],
                  task['start_date'], task['due_date'], task['status'], task['estimated_hours'],
                  task['actual_hours']))
            return cursor.lastrowid
        return self.execute_transaction(op)
    
    def find_by_id(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'project_id': row[1], 'title': row[2], 'description': row[3],
                    'assignee_id': row[4], 'start_date': row[5], 'due_date': row[6], 'status': row[7],
                    'estimated_hours': row[8], 'actual_hours': row[9], 'created_at': row[10]}
        return None
    
    def find_by_project_id(self, project_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,))
        rows = cursor.fetchall()
        return [{'id': row[0], 'project_id': row[1], 'title': row[2], 'description': row[3],
                 'assignee_id': row[4], 'start_date': row[5], 'due_date': row[6], 'status': row[7],
                 'estimated_hours': row[8], 'actual_hours': row[9], 'created_at': row[10]} for row in rows]
    
    def update(self, task, changed_by=None, changes=None):
        def op(cursor):
            cursor.execute('''
            UPDATE tasks SET title = ?, description = ?, assignee_id = ?, start_date = ?, due_date = ?, 
                             status = ?, estimated_hours = ?, actual_hours = ?
            WHERE id = ?
            ''', (task['title'], task['description'], task['assignee_id'], task['start_date'],
                  task['due_date'], task['status'], task['estimated_hours'], task['actual_hours'],
                  task['id']))
            if changes and changed_by:
                for field, (old, new) in changes.items():
                    cursor.execute('''
                    INSERT INTO task_history (task_id, changed_by, field_name, old_value, new_value)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (task['id'], changed_by, field, str(old), str(new)))
        self.execute_transaction(op)
    
    def delete(self, task_id):
        def op(cursor):
            cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.execute_transaction(op)

# Team Member Repository
class TeamMemberRepository(Repository):
    def __init__(self):
        super().__init__('team_members')
    
    def save(self, member):
        def op(cursor):
            cursor.execute('''
            INSERT INTO team_members (user_id, name, role, department, max_workload)
            VALUES (?, ?, ?, ?, ?)
            ''', (member['user_id'], member['name'], member['role'], member['department'], member['max_workload']))
            return cursor.lastrowid
        return self.execute_transaction(op)
    
    def find_by_id(self, member_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM team_members WHERE id = ?', (member_id,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'user_id': row[1], 'name': row[2], 'role': row[3],
                    'department': row[4], 'max_workload': row[5]}
        return None
    
    def find_all_by_user(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM team_members WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        return [{'id': row[0], 'user_id': row[1], 'name': row[2], 'role': row[3],
                 'department': row[4], 'max_workload': row[5]} for row in rows]
    
    def update(self, member):
        def op(cursor):
            cursor.execute('''
            UPDATE team_members SET name = ?, role = ?, department = ?, max_workload = ?
            WHERE id = ?
            ''', (member['name'], member['role'], member['department'], member['max_workload'], member['id']))
        self.execute_transaction(op)
    
    def delete(self, member_id):
        def op(cursor):
            cursor.execute('DELETE FROM team_members WHERE id = ?', (member_id,))
        self.execute_transaction(op)

# Skill Repository
class SkillRepository(Repository):
    def __init__(self):
        super().__init__('skills')
    
    def save(self, skill_name):
        def op(cursor):
            cursor.execute('INSERT OR IGNORE INTO skills (name) VALUES (?)', (skill_name,))
            cursor.execute('SELECT id FROM skills WHERE name = ?', (skill_name,))
            return cursor.fetchone()[0]
        return self.execute_transaction(op)
    
    def find_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM skills WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1]}
        return None
    
    def find_all(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM skills')
        rows = cursor.fetchall()
        return [{'id': row[0], 'name': row[1]} for row in rows]

# Team Member Skills Repository
class TeamMemberSkillsRepository(Repository):
    def __init__(self):
        super().__init__('team_member_skills')
    
    def save(self, team_member_id, skill_id, proficiency):
        def op(cursor):
            cursor.execute('INSERT OR REPLACE INTO team_member_skills (team_member_id, skill_id, proficiency_level) VALUES (?, ?, ?)',
                           (team_member_id, skill_id, proficiency))
        self.execute_transaction(op)
    
    def find_by_member_id(self, member_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT skill_id, proficiency_level FROM team_member_skills WHERE team_member_id = ?', (member_id,))
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}

# Task Skills Repository
class TaskSkillsRepository(Repository):
    def __init__(self):
        super().__init__('task_skills')
    
    def save(self, task_id, skill_id, required_level):
        def op(cursor):
            cursor.execute('INSERT OR REPLACE INTO task_skills (task_id, skill_id, required_level) VALUES (?, ?, ?)',
                           (task_id, skill_id, required_level))
        self.execute_transaction(op)
    
    def find_by_task_id(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT skill_id, required_level FROM task_skills WHERE task_id = ?', (task_id,))
        rows = cursor.fetchall()
        return {row[0]: row[1] for row in rows}

# Task History Repository
class TaskHistoryRepository(Repository):
    def __init__(self):
        super().__init__('task_history')
    
    def find_by_task_id(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM task_history WHERE task_id = ? ORDER BY changed_at DESC', (task_id,))
        rows = cursor.fetchall()
        return [{'id': row[0], 'task_id': row[1], 'changed_by': row[2], 'changed_at': row[3],
                 'field_name': row[4], 'old_value': row[5], 'new_value': row[6]} for row in rows]

# Backup Repository
class BackupRepository(Repository):
    def __init__(self):
        super().__init__('backups')
    
    def save(self, backup):
        def op(cursor):
            cursor.execute('INSERT INTO backups (backup_path, backup_type, description) VALUES (?, ?, ?)',
                           (backup['backup_path'], backup['backup_type'], backup['description']))
        self.execute_transaction(op)
    
    def find_all(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM backups')
        rows = cursor.fetchall()
        return [{'id': row[0], 'backup_path': row[1], 'created_at': row[2], 'backup_type': row[3], 'description': row[4]} for row in rows]

# License Controller
class LicenseController:
    def __init__(self):
        self.repo = LicenseRepository()
    
    def validate_license(self, license_key):
        if not re.match(r'^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$', license_key):
            return False
        
        machine_fingerprint = generate_machine_fingerprint()
        license = self.repo.find_by_key(license_key)
        
        if license['id'] == 0:
            # Simulate internal validation
            if self.internal_validation_algorithm(license_key, machine_fingerprint):
                activation = get_current_datetime()
                expiry = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
                new_license = {'license_key': license_key, 'activation_date': activation, 'expiry_date': expiry,
                               'is_valid': True, 'machine_fingerprint': machine_fingerprint}
                self.repo.save(new_license)
                return True
            return False
        
        is_not_expired = get_current_datetime() < license['expiry_date']
        is_machine_match = machine_fingerprint == license['machine_fingerprint']
        is_valid = license['is_valid'] and is_not_expired and is_machine_match
        
        if not is_valid:
            license['is_valid'] = False
            self.repo.update(license)
        
        return is_valid
    
    def internal_validation_algorithm(self, key, fingerprint):
        # Placeholder
        return True

# Backup Manager
class BackupManager:
    def __init__(self):
        self.backup_repo = BackupRepository()
    
    def create_backup(self, backup_path, backup_type='manual', description=''):
        conn = DatabaseConnection.get_connection()
        try:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            backup_conn = sqlite3.connect(backup_path)
            query = ''.join(line for line in conn.iterdump())
            backup_conn.executescript(query)
            backup_conn.close()
            
            # Record metadata
            backup = {'backup_path': backup_path, 'backup_type': backup_type, 'description': description}
            self.backup_repo.save(backup)
            return True
        except Exception as e:
            print(f"Backup failed: {e}")
            return False
    
    def recover_from_backup(self, backup_path):
        if messagebox.askyesno("Confirm Recovery", "This will overwrite current data. Continue?"):
            try:
                # Simple file replacement
                current_db = 'teamaxis.db'
                os.replace(backup_path, current_db)
                # Reconnect
                DatabaseConnection._connection = None
                return True
            except Exception as e:
                print(f"Recovery failed: {e}")
                return False

# Resource Allocation Engine
class ResourceAllocationEngine:
    def __init__(self):
        self.team_repo = TeamMemberRepository()
        self.task_repo = TaskRepository()
        self.member_skills_repo = TeamMemberSkillsRepository()
        self.task_skills_repo = TaskSkillsRepository()
    
    def is_at_max_workload(self, member_id):
        member = self.team_repo.find_by_id(member_id)
        if not member:
            return True
        tasks = self.task_repo.find_by_assignee_id(member_id)  # Assuming added method
        current_hours = sum(t['estimated_hours'] for t in tasks if t['status'] != 'completed')
        return current_hours >= member['max_workload']
    
    def calculate_workload_percentage(self, member_id):
        member = self.team_repo.find_by_id(member_id)
        if not member:
            return 100
        tasks = self.task_repo.find_by_assignee_id(member_id)
        current_hours = sum(t['estimated_hours'] for t in tasks if t['status'] != 'completed')
        return (current_hours / member['max_workload']) * 100 if member['max_workload'] > 0 else 0
    
    def calculate_skill_match(self, member_id, required_skills):
        member_skills = self.member_skills_repo.find_by_member_id(member_id)
        match_score = 0
        total = 0
        for skill_id, req_level in required_skills.items():
            prof = member_skills.get(skill_id, 0)
            match_score += min(prof, req_level) / req_level * 100 if req_level > 0 else 0
            total += 1
        return (match_score / total) if total > 0 else 0
    
    def get_recommended_assignees(self, task_id):
        required_skills = self.task_skills_repo.find_by_task_id(task_id)
        members = self.team_repo.find_all()  # Assuming find_all method added
        recommendations = []
        for member in members:
            if self.is_at_max_workload(member['id']):
                continue
            skill_match = self.calculate_skill_match(member['id'], required_skills)
            workload_perc = self.calculate_workload_percentage(member['id'])
            score = 0.7 * skill_match + 0.3 * (100 - workload_perc)
            if score > 50:
                recommendations.append({
                    'id': member['id'],
                    'name': member['name'],
                    'recommendation_score': score,
                    'skill_match_score': skill_match,
                    'workload_percentage': workload_perc
                })
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommendations

# Add missing methods to repositories
class TeamMemberRepository(TeamMemberRepository):  # Extend
    def find_all(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM team_members')
        rows = cursor.fetchall()
        return [{'id': row[0], 'user_id': row[1], 'name': row[2], 'role': row[3],
                 'department': row[4], 'max_workload': row[5]} for row in rows]
    
    def find_by_assignee_id(self, assignee_id):  # Wait, this is for tasks
        pass  # Mistake, move to TaskRepository

class TaskRepository(TaskRepository):
    def find_by_assignee_id(self, assignee_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE assignee_id = ?', (assignee_id,))
        rows = cursor.fetchall()
        return [{'id': row[0], 'project_id': row[1], 'title': row[2], 'description': row[3],
                 'assignee_id': row[4], 'start_date': row[5], 'due_date': row[6], 'status': row[7],
                 'estimated_hours': row[8], 'actual_hours': row[9], 'created_at': row[10]} for row in rows]

# Risk Calculator
class RiskCalculator:
    def __init__(self):
        self.project_repo = ProjectRepository()
        self.task_repo = TaskRepository()
        self.team_repo = TeamMemberRepository()
        self.allocation_engine = ResourceAllocationEngine()
    
    def calculate_schedule_deviation(self, tasks):
        total_deviation = 0
        count = 0
        today = datetime.datetime.now()
        for task in tasks:
            due = parse_date(task['due_date'])
            if due and due < today and task['status'] != 'completed':
                deviation = (today - due).days
                total_deviation += deviation
                count += 1
        return (total_deviation / count) if count > 0 else 0
    
    def calculate_resource_utilization(self, project_id):
        tasks = self.task_repo.find_by_project_id(project_id)
        assignees = set(t['assignee_id'] for t in tasks if t['assignee_id'])
        total_util = 0
        count = 0
        for assignee_id in assignees:
            util = self.allocation_engine.calculate_workload_percentage(assignee_id)
            total_util += util
            count += 1
        return (total_util / count) if count > 0 else 0
    
    def calculate_project_risk(self, project_id):
        project = self.project_repo.find_by_id(project_id)
        if not project:
            return 0
        tasks = self.task_repo.find_by_project_id(project_id)
        schedule_deviation = self.calculate_schedule_deviation(tasks)
        resource_utilization = self.calculate_resource_utilization(project_id)
        risk_score = 0.6 * schedule_deviation + 0.4 * resource_utilization
        project['risk_score'] = risk_score
        self.project_repo.update(project)
        return risk_score

# Cache
class Cache:
    _cache = {}
    _timers = {}

    @classmethod
    def get(cls, key):
        return cls._cache.get(key)
    
    @classmethod
    def set(cls, key, value, ttl=300):
        cls._cache[key] = value
        if key in cls._timers:
            cls._timers[key].cancel()
        timer = threading.Timer(ttl, cls._expire, args=(key,))
        timer.start()
        cls._timers[key] = timer
    
    @classmethod
    def _expire(cls, key):
        cls._cache.pop(key, None)
        cls._timers.pop(key, None)

# Project Service
class ProjectService:
    def __init__(self):
        self.repo = ProjectRepository()
        self.risk_calc = RiskCalculator()
    
    def create_project(self, name, description, start_date, end_date, created_by):
        project = {'name': name, 'description': description, 'start_date': start_date,
                   'end_date': end_date, 'created_by': created_by}
        project_id = self.repo.save(project)
        return project_id
    
    def get_projects(self, user_id):
        cache_key = f"projects_{user_id}"
        cached = Cache.get(cache_key)
        if cached:
            return cached
        projects = self.repo.find_all_by_user(user_id)
        Cache.set(cache_key, projects)
        return projects
    
    def update_project(self, project_id, name, description, start_date, end_date):
        project = self.repo.find_by_id(project_id)
        if project:
            project['name'] = name
            project['description'] = description
            project['start_date'] = start_date
            project['end_date'] = end_date
            self.repo.update(project)
            self.risk_calc.calculate_project_risk(project_id)
    
    def delete_project(self, project_id):
        self.repo.delete(project_id)

# Task Service
class TaskService:
    def __init__(self):
        self.repo = TaskRepository()
        self.task_skills_repo = TaskSkillsRepository()
        self.history_repo = TaskHistoryRepository()
    
    def create_task(self, project_id, title, description, due_date, estimated_hours, skills=None):
        task = {'project_id': project_id, 'title': title, 'description': description,
                'assignee_id': None, 'start_date': None, 'due_date': due_date,
                'status': 'pending', 'estimated_hours': estimated_hours, 'actual_hours': 0}
        task_id = self.repo.save(task)
        if skills:
            for skill_id, level in skills.items():
                self.task_skills_repo.save(task_id, skill_id, level)
        return task_id
    
    def get_tasks(self, project_id):
        cache_key = f"tasks_{project_id}"
        cached = Cache.get(cache_key)
        if cached:
            return cached
        tasks = self.repo.find_by_project_id(project_id)
        Cache.set(cache_key, tasks)
        return tasks
    
    def update_task(self, task_id, updates, changed_by):
        task = self.repo.find_by_id(task_id)
        if task:
            changes = {}
            for field, new_val in updates.items():
                old_val = task.get(field)
                if old_val != new_val:
                    changes[field] = (old_val, new_val)
                    task[field] = new_val
            self.repo.update(task, changed_by, changes)
    
    def delete_task(self, task_id):
        self.repo.delete(task_id)
    
    def get_task_history(self, task_id):
        return self.history_repo.find_by_task_id(task_id)

# Team Member Service
class TeamMemberService:
    def __init__(self):
        self.repo = TeamMemberRepository()
        self.skills_repo = SkillRepository()
        self.member_skills_repo = TeamMemberSkillsRepository()
    
    def create_member(self, user_id, name, role, department, max_workload=40, skills=None):
        member = {'user_id': user_id, 'name': name, 'role': role, 'department': department, 'max_workload': max_workload}
        member_id = self.repo.save(member)
        if skills:
            for skill_name, prof in skills.items():
                skill = self.skills_repo.find_by_name(skill_name)
                if not skill:
                    skill_id = self.skills_repo.save(skill_name)
                else:
                    skill_id = skill['id']
                self.member_skills_repo.save(member_id, skill_id, prof)
        return member_id
    
    def get_members(self, user_id):
        cache_key = f"members_{user_id}"
        cached = Cache.get(cache_key)
        if cached:
            return cached
        members = self.repo.find_all_by_user(user_id)
        Cache.set(cache_key, members)
        return members
    
    def update_member(self, member_id, name, role, department, max_workload):
        member = self.repo.find_by_id(member_id)
        if member:
            member['name'] = name
            member['role'] = role
            member['department'] = department
            member['max_workload'] = max_workload
            self.repo.update(member)
    
    def delete_member(self, member_id):
        self.repo.delete(member_id)
    
    def get_skills(self):
        return self.skills_repo.find_all()

# UI Components
class TeamAxisApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TeamAxis")
        self.user_repo = UserRepository()
        self.license_controller = LicenseController()
        self.project_service = ProjectService()
        self.task_service = TaskService()
        self.team_service = TeamMemberService()
        self.allocation_engine = ResourceAllocationEngine()
        self.backup_manager = BackupManager()
        self.risk_calc = RiskCalculator()
        self.is_licensed = False
        self.current_user = None
        self.current_project_id = None
        self.current_task_id = None
        self.show_login()
    
    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_login(self):
        self.clear_frame()
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
            self.user_repo.update_last_login(user['id'])
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
        self.clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()
        
        ttk.Label(frame, text="License Key:").grid(row=0, column=0)
        key_entry = ttk.Entry(frame)
        key_entry.grid(row=0, column=1)
        
        ttk.Button(frame, text="Validate", command=lambda: self.validate_and_proceed(key_entry.get())).grid(row=1, column=0)
        ttk.Button(frame, text="Load from File", command=self.load_license_file).grid(row=1, column=1)
    
    def load_license_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as f:
                key = f.read().strip()
            self.validate_and_proceed(key)
    
    def validate_and_proceed(self, key):
        if self.license_controller.validate_license(key):
            self.is_licensed = True
            messagebox.showinfo("Success", "License valid")
            self.show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid license")
    
    def show_dashboard(self):
        if not self.is_licensed:
            return
        self.clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()
        
        ttk.Label(frame, text="Projects").grid(row=0, column=0)
        self.project_tree = ttk.Treeview(frame, columns=('id', 'name', 'risk'), show='headings')
        self.project_tree.heading('id', text='ID')
        self.project_tree.heading('name', text='Name')
        self.project_tree.heading('risk', text='Risk Score')
        self.project_tree.grid(row=1, column=0, columnspan=2)
        
        self.load_projects()
        
        ttk.Button(frame, text="Create Project", command=self.show_create_project).grid(row=2, column=0)
        ttk.Button(frame, text="View Project", command=self.view_selected_project).grid(row=2, column=1)
        ttk.Button(frame, text="Team Management", command=self.show_team_management).grid(row=3, column=0)
        ttk.Button(frame, text="Backup", command=self.perform_backup).grid(row=4, column=0)
        ttk.Button(frame, text="Recover", command=self.perform_recovery).grid(row=4, column=1)
    
    def load_projects(self):
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        projects = self.project_service.get_projects(self.current_user['id'])
        for proj in projects:
            self.project_tree.insert('', 'end', values=(proj['id'], proj['name'], proj['risk_score']))
    
    def show_create_project(self):
        window = tk.Toplevel(self.root)
        window.title("Create Project")
        
        ttk.Label(window, text="Name:").grid(row=0, column=0)
        name_entry = ttk.Entry(window)
        name_entry.grid(row=0, column=1)
        
        ttk.Label(window, text="Description:").grid(row=1, column=0)
        desc_entry = ttk.Entry(window)
        desc_entry.grid(row=1, column=1)
        
        ttk.Label(window, text="Start Date (YYYY-MM-DD):").grid(row=2, column=0)
        start_entry = ttk.Entry(window)
        start_entry.grid(row=2, column=1)
        
        ttk.Label(window, text="End Date (YYYY-MM-DD):").grid(row=3, column=0)
        end_entry = ttk.Entry(window)
        end_entry.grid(row=3, column=1)
        
        ttk.Button(window, text="Save", command=lambda: self.save_project(
            name_entry.get(), desc_entry.get(), start_entry.get(), end_entry.get(), window
        )).grid(row=4, column=0)
    
    def save_project(self, name, desc, start, end, window):
        if name and start and end:
            self.project_service.create_project(name, desc, start + 'T00:00:00', end + 'T00:00:00', self.current_user['id'])
            window.destroy()
            self.load_projects()
        else:
            messagebox.showerror("Error", "Missing fields")
    
    def view_selected_project(self):
        selected = self.project_tree.focus()
        if selected:
            values = self.project_tree.item(selected, 'values')
            self.current_project_id = int(values[0])
            self.show_project_detail()
    
    def show_project_detail(self):
        self.clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()
        
        project = self.project_service.repo.find_by_id(self.current_project_id)
        ttk.Label(frame, text=f"Project: {project['name']} (Risk: {project['risk_score']})").grid(row=0, column=0, columnspan=3)
        
        ttk.Button(frame, text="Calculate Risk", command=lambda: self.calculate_risk(self.current_project_id)).grid(row=1, column=0)
        ttk.Button(frame, text="Back to Dashboard", command=self.show_dashboard).grid(row=1, column=1)
        
        ttk.Label(frame, text="Tasks").grid(row=2, column=0)
        self.task_tree = ttk.Treeview(frame, columns=('id', 'title', 'status', 'due_date', 'assignee'), show='headings')
        self.task_tree.heading('id', text='ID')
        self.task_tree.heading('title', text='Title')
        self.task_tree.heading('status', text='Status')
        self.task_tree.heading('due_date', text='Due Date')
        self.task_tree.heading('assignee', text='Assignee')
        self.task_tree.grid(row=3, column=0, columnspan=3)
        
        self.load_tasks()
        
        ttk.Button(frame, text="Create Task", command=self.show_create_task).grid(row=4, column=0)
        ttk.Button(frame, text="Edit Task", command=self.edit_selected_task).grid(row=4, column=1)
        ttk.Button(frame, text="Delete Task", command=self.delete_selected_task).grid(row=4, column=2)
        ttk.Button(frame, text="View Task History", command=self.view_task_history).grid(row=5, column=0)
    
    def load_tasks(self):
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        tasks = self.task_service.get_tasks(self.current_project_id)
        for task in tasks:
            assignee = self.team_service.repo.find_by_id(task['assignee_id']) if task['assignee_id'] else {'name': 'Unassigned'}
            self.task_tree.insert('', 'end', values=(task['id'], task['title'], task['status'], task['due_date'][:10], assignee['name']))
    
    def show_create_task(self):
        window = tk.Toplevel(self.root)
        window.title("Create Task")
        
        ttk.Label(window, text="Title:").grid(row=0, column=0)
        title_entry = ttk.Entry(window)
        title_entry.grid(row=0, column=1)
        
        ttk.Label(window, text="Description:").grid(row=1, column=0)
        desc_entry = ttk.Entry(window)
        desc_entry.grid(row=1, column=1)
        
        ttk.Label(window, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0)
        due_entry = ttk.Entry(window)
        due_entry.grid(row=2, column=1)
        
        ttk.Label(window, text="Estimated Hours:").grid(row=3, column=0)
        est_entry = ttk.Entry(window)
        est_entry.grid(row=3, column=1)
        
        # Skills
        ttk.Label(window, text="Required Skills (name:level, comma separated):").grid(row=4, column=0)
        skills_entry = ttk.Entry(window)
        skills_entry.grid(row=4, column=1)
        
        ttk.Button(window, text="Save", command=lambda: self.save_task(
            title_entry.get(), desc_entry.get(), due_entry.get(), est_entry.get(), skills_entry.get(), window
        )).grid(row=5, column=0)
    
    def save_task(self, title, desc, due, est, skills_str, window):
        if title and due and est:
            skills = {}
            if skills_str:
                for part in skills_str.split(','):
                    name, level = part.split(':')
                    skill = self.team_service.skills_repo.find_by_name(name.strip())
                    if not skill:
                        skill_id = self.team_service.skills_repo.save(name.strip())
                    else:
                        skill_id = skill['id']
                    skills[skill_id] = int(level.strip())
            self.task_service.create_task(self.current_project_id, title, desc, due + 'T00:00:00', float(est), skills)
            window.destroy()
            self.load_tasks()
        else:
            messagebox.showerror("Error", "Missing fields")
    
    def edit_selected_task(self):
        selected = self.task_tree.focus()
        if selected:
            values = self.task_tree.item(selected, 'values')
            task_id = int(values[0])
            self.current_task_id = task_id
            task = self.task_service.repo.find_by_id(task_id)
            recommendations = self.allocation_engine.get_recommended_assignees(task_id)
            window = tk.Toplevel(self.root)
            window.title("Edit Task")
            
            ttk.Label(window, text="Title:").grid(row=0, column=0)
            title_entry = ttk.Entry(window)
            title_entry.insert(0, task['title'])
            title_entry.grid(row=0, column=1)
            
            ttk.Label(window, text="Description:").grid(row=1, column=0)
            desc_entry = ttk.Entry(window)
            desc_entry.insert(0, task['description'] or '')
            desc_entry.grid(row=1, column=1)
            
            ttk.Label(window, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0)
            due_entry = ttk.Entry(window)
            due_entry.insert(0, task['due_date'][:10] if task['due_date'] else '')
            due_entry.grid(row=2, column=1)
            
            ttk.Label(window, text="Status:").grid(row=3, column=0)
            status_combo = ttk.Combobox(window, values=['pending', 'in_progress', 'completed', 'blocked'])
            status_combo.set(task['status'])
            status_combo.grid(row=3, column=1)
            
            ttk.Label(window, text="Actual Hours:").grid(row=4, column=0)
            actual_entry = ttk.Entry(window)
            actual_entry.insert(0, task['actual_hours'])
            actual_entry.grid(row=4, column=1)
            
            ttk.Label(window, text="Assignee:").grid(row=5, column=0)
            assignee_combo = ttk.Combobox(window, values=[r['name'] for r in recommendations])
            current_assignee = self.team_service.repo.find_by_id(task['assignee_id'])
            if current_assignee:
                assignee_combo.set(current_assignee['name'])
            assignee_combo.grid(row=5, column=1)
            
            ttk.Button(window, text="Update", command=lambda: self.update_task(
                task_id, title_entry.get(), desc_entry.get(), due_entry.get(), status_combo.get(),
                actual_entry.get(), assignee_combo.get(), recommendations, window
            )).grid(row=6, column=0)
    
    def update_task(self, task_id, title, desc, due, status, actual, assignee_name, recommendations, window):
        assignee_id = next((r['id'] for r in recommendations if r['name'] == assignee_name), None)
        updates = {
            'title': title,
            'description': desc,
            'due_date': due + 'T00:00:00',
            'status': status,
            'actual_hours': float(actual),
            'assignee_id': assignee_id
        }
        self.task_service.update_task(task_id, updates, self.current_user['id'])
        window.destroy()
        self.load_tasks()
    
    def delete_selected_task(self):
        selected = self.task_tree.focus()
        if selected:
            values = self.task_tree.item(selected, 'values')
            task_id = int(values[0])
            if messagebox.askyesno("Confirm", "Delete task?"):
                self.task_service.delete_task(task_id)
                self.load_tasks()
    
    def view_task_history(self):
        selected = self.task_tree.focus()
        if selected:
            values = self.task_tree.item(selected, 'values')
            task_id = int(values[0])
            history = self.task_service.get_task_history(task_id)
            window = tk.Toplevel(self.root)
            window.title("Task History")
            tree = ttk.Treeview(window, columns=('changed_at', 'field', 'old', 'new'), show='headings')
            tree.heading('changed_at', text='Changed At')
            tree.heading('field', text='Field')
            tree.heading('old', text='Old Value')
            tree.heading('new', text='New Value')
            tree.grid()
            for h in history:
                tree.insert('', 'end', values=(h['changed_at'], h['field_name'], h['old_value'], h['new_value']))
    
    def calculate_risk(self, project_id):
        score = self.risk_calc.calculate_project_risk(project_id)
        messagebox.showinfo("Risk Score", f"Calculated risk: {score}")
        self.show_project_detail()
    
    def show_team_management(self):
        self.clear_frame()
        frame = ttk.Frame(self.root, padding=20)
        frame.grid()
        
        ttk.Label(frame, text="Team Members").grid(row=0, column=0)
        self.member_tree = ttk.Treeview(frame, columns=('id', 'name', 'role', 'department', 'max_workload'), show='headings')
        self.member_tree.heading('id', text='ID')
        self.member_tree.heading('name', text='Name')
        self.member_tree.heading('role', text='Role')
        self.member_tree.heading('department', text='Department')
        self.member_tree.heading('max_workload', text='Max Workload')
        self.member_tree.grid(row=1, column=0, columnspan=2)
        
        self.load_members()
        
        ttk.Button(frame, text="Create Member", command=self.show_create_member).grid(row=2, column=0)
        ttk.Button(frame, text="Edit Member", command=self.edit_selected_member).grid(row=2, column=1)
        ttk.Button(frame, text="Back to Dashboard", command=self.show_dashboard).grid(row=3, column=0)
    
    def load_members(self):
        for item in self.member_tree.get_children():
            self.member_tree.delete(item)
        members = self.team_service.get_members(self.current_user['id'])
        for m in members:
            self.member_tree.insert('', 'end', values=(m['id'], m['name'], m['role'], m['department'], m['max_workload']))
    
    def show_create_member(self):
        window = tk.Toplevel(self.root)
        window.title("Create Team Member")
        
        ttk.Label(window, text="Name:").grid(row=0, column=0)
        name_entry = ttk.Entry(window)
        name_entry.grid(row=0, column=1)
        
        ttk.Label(window, text="Role:").grid(row=1, column=0)
        role_entry = ttk.Entry(window)
        role_entry.grid(row=1, column=1)
        
        ttk.Label(window, text="Department:").grid(row=2, column=0)
        dept_entry = ttk.Entry(window)
        dept_entry.grid(row=2, column=1)
        
        ttk.Label(window, text="Max Workload (hours):").grid(row=3, column=0)
        max_entry = ttk.Entry(window)
        max_entry.insert(0, '40')
        max_entry.grid(row=3, column=1)
        
        ttk.Label(window, text="Skills (name:level, comma separated):").grid(row=4, column=0)
        skills_entry = ttk.Entry(window)
        skills_entry.grid(row=4, column=1)
        
        ttk.Button(window, text="Save", command=lambda: self.save_member(
            name_entry.get(), role_entry.get(), dept_entry.get(), max_entry.get(), skills_entry.get(), window
        )).grid(row=5, column=0)
    
    def save_member(self, name, role, dept, max_w, skills_str, window):
        if name:
            skills = {}
            if skills_str:
                for part in skills_str.split(','):
                    n, l = part.split(':')
                    skills[n.strip()] = int(l.strip())
            self.team_service.create_member(self.current_user['id'], name, role, dept, int(max_w or 40), skills)
            window.destroy()
            self.load_members()
        else:
            messagebox.showerror("Error", "Missing name")
    
    def edit_selected_member(self):
        selected = self.member_tree.focus()
        if selected:
            values = self.member_tree.item(selected, 'values')
            member_id = int(values[0])
            member = self.team_service.repo.find_by_id(member_id)
            window = tk.Toplevel(self.root)
            window.title("Edit Team Member")
            
            ttk.Label(window, text="Name:").grid(row=0, column=0)
            name_entry = ttk.Entry(window)
            name_entry.insert(0, member['name'])
            name_entry.grid(row=0, column=1)
            
            ttk.Label(window, text="Role:").grid(row=1, column=0)
            role_entry = ttk.Entry(window)
            role_entry.insert(0, member['role'] or '')
            role_entry.grid(row=1, column=1)
            
            ttk.Label(window, text="Department:").grid(row=2, column=0)
            dept_entry = ttk.Entry(window)
            dept_entry.insert(0, member['department'] or '')
            dept_entry.grid(row=2, column=1)
            
            ttk.Label(window, text="Max Workload:").grid(row=3, column=0)
            max_entry = ttk.Entry(window)
            max_entry.insert(0, member['max_workload'])
            max_entry.grid(row=3, column=1)
            
            ttk.Button(window, text="Update", command=lambda: self.update_member(
                member_id, name_entry.get(), role_entry.get(), dept_entry.get(), max_entry.get(), window
            )).grid(row=4, column=0)
    
    def update_member(self, member_id, name, role, dept, max_w, window):
        self.team_service.update_member(member_id, name, role, dept, int(max_w))
        window.destroy()
        self.load_members()
    
    def perform_backup(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database", "*.db")])
        if file_path:
            if self.backup_manager.create_backup(file_path):
                messagebox.showinfo("Success", "Backup created")
    
    def perform_recovery(self):
        file_path = filedialog.askopenfilename(filetypes=[("Database", "*.db")])
        if file_path:
            if self.backup_manager.recover_from_backup(file_path):
                messagebox.showinfo("Success", "Recovery complete. Restart app.")
                self.root.quit()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    create_schema()
    app = TeamAxisApp()
    app.run()