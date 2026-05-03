"""
Tests for features/risk_warning.py
"""

import pytest
from datetime import datetime, timedelta
from features.risk_warning import RiskWarningSystem

class TestRiskWarningSystem:
    """Test RiskWarningSystem class."""
    
    def test_get_all_risks_all_projects(self, temp_db, sample_project):
        """Test getting all risks across all projects."""
        temp_db.create_risk(sample_project.project_id, 'Risk 1', 'high')
        temp_db.create_risk(sample_project.project_id, 'Risk 2', 'medium')
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        risks = risk_system.get_all_risks()
        assert len(risks) >= 2
    
    def test_get_all_risks_specific_project(self, temp_db, sample_project):
        """Test getting risks for specific project."""
        temp_db.create_risk(sample_project.project_id, 'Risk 1', 'high')
        
        # Create another project and risk
        project2_id = temp_db.create_project('Project 2', 'Desc', '2024-01-01', '2024-12-31')
        temp_db.create_risk(project2_id, 'Risk 2', 'medium')
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        risks = risk_system.get_all_risks(sample_project.project_id)
        assert len(risks) >= 1
        assert all(r.project_id == sample_project.project_id for r in risks)
    
    def test_get_critical_risks(self, temp_db, sample_project):
        """Test getting critical and high severity risks."""
        temp_db.create_risk(sample_project.project_id, 'Critical Risk', 'critical', 'open')
        temp_db.create_risk(sample_project.project_id, 'High Risk', 'high', 'open')
        temp_db.create_risk(sample_project.project_id, 'Medium Risk', 'medium', 'open')
        temp_db.create_risk(sample_project.project_id, 'Closed Risk', 'critical', 'closed')
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        critical_risks = risk_system.get_critical_risks()
        assert len(critical_risks) >= 2
        assert all(r.severity in ['high', 'critical'] for r in critical_risks)
        assert all(r.status == 'open' for r in critical_risks)
    
    def test_get_open_risks(self, temp_db, sample_project):
        """Test getting all open risks."""
        temp_db.create_risk(sample_project.project_id, 'Open Risk 1', 'high', 'open')
        temp_db.create_risk(sample_project.project_id, 'Open Risk 2', 'medium', 'open')
        temp_db.create_risk(sample_project.project_id, 'Closed Risk', 'high', 'closed')
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        open_risks = risk_system.get_open_risks()
        assert len(open_risks) >= 2
        assert all(r.status == 'open' for r in open_risks)
    
    def test_analyze_project_risks(self, temp_db, sample_project, sample_user):
        """Test analyzing project risks."""
        # Create risks
        temp_db.create_risk(sample_project.project_id, 'Critical Risk', 'critical', 'open')
        temp_db.create_risk(sample_project.project_id, 'High Risk', 'high', 'open')
        
        # Create tasks
        temp_db.create_task(sample_project.project_id, 'Blocked Task 1', 'Desc', sample_user.user_id, 'blocked')
        temp_db.create_task(sample_project.project_id, 'Blocked Task 2', 'Desc', sample_user.user_id, 'blocked')
        temp_db.create_task(sample_project.project_id, 'Blocked Task 3', 'Desc', sample_user.user_id, 'blocked')
        temp_db.create_task(sample_project.project_id, 'Blocked Task 4', 'Desc', sample_user.user_id, 'blocked')
        
        # Create overdue task
        overdue_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        temp_db.create_task(sample_project.project_id, 'Overdue Task', 'Desc', sample_user.user_id, 'pending', 'medium', overdue_date)
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        analysis = risk_system.analyze_project_risks(sample_project.project_id)
        assert analysis is not None
        assert analysis['project_id'] == sample_project.project_id
        assert analysis['total_risks'] >= 2
        assert analysis['critical_risks'] >= 1
        assert analysis['high_risks'] >= 1
        assert analysis['blocked_tasks'] >= 4
        assert analysis['overdue_tasks'] >= 1
        assert len(analysis['warnings']) > 0
    
    def test_analyze_project_risks_nonexistent_project(self, temp_db):
        """Test analyzing risks for non-existent project."""
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        analysis = risk_system.analyze_project_risks(99999)
        assert analysis is None
    
    def test_count_overdue_tasks(self, temp_db, sample_project, sample_user):
        """Test counting overdue tasks."""
        # Create overdue task
        overdue_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        temp_db.create_task(sample_project.project_id, 'Overdue Task', 'Desc', sample_user.user_id, 'pending', 'medium', overdue_date)
        
        # Create future task
        future_date = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        temp_db.create_task(sample_project.project_id, 'Future Task', 'Desc', sample_user.user_id, 'pending', 'medium', future_date)
        
        # Create completed overdue task (should not count)
        temp_db.create_task(sample_project.project_id, 'Completed Overdue', 'Desc', sample_user.user_id, 'completed', 'medium', overdue_date)
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        tasks = temp_db.get_tasks_by_project(sample_project.project_id)
        overdue_count = risk_system._count_overdue_tasks(tasks)
        assert overdue_count >= 1
    
    def test_get_risk_summary(self, temp_db, sample_project):
        """Test getting risk summary."""
        temp_db.create_risk(sample_project.project_id, 'Critical Risk', 'critical', 'open')
        temp_db.create_risk(sample_project.project_id, 'High Risk', 'high', 'open')
        temp_db.create_risk(sample_project.project_id, 'Medium Risk', 'medium', 'open')
        temp_db.create_risk(sample_project.project_id, 'Low Risk', 'low', 'open')
        temp_db.create_risk(sample_project.project_id, 'Closed Risk', 'critical', 'closed')
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        summary = risk_system.get_risk_summary()
        assert summary['total_projects'] >= 1
        assert summary['total_risks'] >= 5
        assert summary['open_risks'] >= 4
        assert summary['by_severity']['critical'] >= 1
        assert summary['by_severity']['high'] >= 1
        assert summary['by_severity']['medium'] >= 1
        assert summary['by_severity']['low'] >= 1
    
    def test_create_risk_alert(self, temp_db, sample_project):
        """Test creating a risk alert."""
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        risk_id = risk_system.create_risk_alert(sample_project.project_id, 'Test Risk', 'high')
        assert risk_id is not None
        
        risks = temp_db.get_all_risks()
        created_risk = next(r for r in risks if r.risk_id == risk_id)
        assert created_risk.description == 'Test Risk'
        assert created_risk.severity == 'high'
        assert created_risk.status == 'open'
    
    def test_get_immediate_alerts(self, temp_db, sample_project):
        """Test getting immediate alerts."""
        temp_db.create_risk(sample_project.project_id, 'Critical Risk', 'critical', 'open')
        temp_db.create_risk(sample_project.project_id, 'High Risk', 'high', 'open')
        
        risk_system = RiskWarningSystem()
        risk_system.db_manager = temp_db
        
        alerts = risk_system.get_immediate_alerts()
        assert len(alerts) > 0
        assert any('CRITICAL' in alert['type'] for alert in alerts)

