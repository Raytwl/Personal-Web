"""
Data models for TeamAxis project management system.
"""

class User:
    """User model for authentication."""
    def __init__(self, user_id, username, password_hash, email, role='user'):
        self.user_id = user_id
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role

class Project:
    """Project model."""
    def __init__(self, project_id, name, description, start_date, end_date, status='active', progress=0):
        self.project_id = project_id
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.status = status  # active, completed, on_hold, cancelled
        self.progress = progress  # 0-100

class Task:
    """Task model."""
    def __init__(self, task_id, project_id, name, description, assignee_id, status='pending', 
                 priority='medium', due_date=None, progress=0):
        self.task_id = task_id
        self.project_id = project_id
        self.name = name
        self.description = description
        self.assignee_id = assignee_id
        self.status = status  # pending, in_progress, completed, blocked
        self.priority = priority  # low, medium, high, critical
        self.due_date = due_date
        self.progress = progress  # 0-100

class License:
    """License model."""
    def __init__(self, license_id, license_key, user_id, issue_date, expiry_date, status='active'):
        self.license_id = license_id
        self.license_key = license_key
        self.user_id = user_id
        self.issue_date = issue_date
        self.expiry_date = expiry_date
        self.status = status  # active, expired, revoked

class Risk:
    """Risk model for risk warning system."""
    def __init__(self, risk_id, project_id, description, severity='medium', status='open', mitigation=None):
        self.risk_id = risk_id
        self.project_id = project_id
        self.description = description
        self.severity = severity  # low, medium, high, critical
        self.status = status  # open, mitigated, closed
        self.mitigation = mitigation

