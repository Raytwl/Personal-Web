"""
Risk warning system module for TeamAxis.
Monitors and alerts about project risks.
"""

from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

class RiskWarningSystem:
    """Manages risk warnings and alerts."""
    
    def __init__(self):
        """Initialize risk warning system."""
        self.db_manager = DatabaseManager()
    
    def get_all_risks(self, project_id=None):
        """Get all risks, optionally filtered by project."""
        if project_id:
            return self.db_manager.get_risks_by_project(project_id)
        return self.db_manager.get_all_risks()
    
    def get_critical_risks(self, project_id=None):
        """Get all critical and high severity risks."""
        risks = self.get_all_risks(project_id)
        return [r for r in risks if r.severity in ['high', 'critical'] and r.status == 'open']
    
    def get_open_risks(self, project_id=None):
        """Get all open risks."""
        risks = self.get_all_risks(project_id)
        return [r for r in risks if r.status == 'open']
    
    def analyze_project_risks(self, project_id):
        """Analyze risks for a specific project."""
        risks = self.get_all_risks(project_id)
        tasks = self.db_manager.get_tasks_by_project(project_id)
        project = None
        for p in self.db_manager.get_all_projects():
            if p.project_id == project_id:
                project = p
                break
        
        if not project:
            return None
        
        analysis = {
            'project_id': project_id,
            'project_name': project.name,
            'total_risks': len(risks),
            'open_risks': len([r for r in risks if r.status == 'open']),
            'critical_risks': len([r for r in risks if r.severity == 'critical']),
            'high_risks': len([r for r in risks if r.severity == 'high']),
            'blocked_tasks': len([t for t in tasks if t.status == 'blocked']),
            'overdue_tasks': self._count_overdue_tasks(tasks),
            'warnings': []
        }
        
        # Generate warnings
        if analysis['critical_risks'] > 0:
            analysis['warnings'].append(
                f"CRITICAL: {analysis['critical_risks']} critical risk(s) require immediate attention!"
            )
        
        if analysis['high_risks'] > 0:
            analysis['warnings'].append(
                f"WARNING: {analysis['high_risks']} high severity risk(s) detected."
            )
        
        if analysis['blocked_tasks'] > 3:
            analysis['warnings'].append(
                f"WARNING: {analysis['blocked_tasks']} blocked tasks may indicate project issues."
            )
        
        if analysis['overdue_tasks'] > 0:
            analysis['warnings'].append(
                f"WARNING: {analysis['overdue_tasks']} overdue task(s) detected."
            )
        
        if project.progress < 30 and project.status == 'active':
            days_since_start = (datetime.now().date() - 
                              datetime.strptime(project.start_date, '%Y-%m-%d').date()).days
            if days_since_start > 30:
                analysis['warnings'].append(
                    "WARNING: Project progress is low after significant time has passed."
                )
        
        return analysis
    
    def _count_overdue_tasks(self, tasks):
        """Count overdue tasks."""
        today = datetime.now().date()
        overdue = 0
        for task in tasks:
            if task.due_date and task.status != 'completed':
                due = datetime.strptime(task.due_date, '%Y-%m-%d').date()
                if due < today:
                    overdue += 1
        return overdue
    
    def get_risk_summary(self):
        """Get overall risk summary across all projects."""
        all_risks = self.get_all_risks()
        all_projects = self.db_manager.get_all_projects()
        
        summary = {
            'total_projects': len(all_projects),
            'total_risks': len(all_risks),
            'open_risks': len([r for r in all_risks if r.status == 'open']),
            'by_severity': {
                'critical': len([r for r in all_risks if r.severity == 'critical' and r.status == 'open']),
                'high': len([r for r in all_risks if r.severity == 'high' and r.status == 'open']),
                'medium': len([r for r in all_risks if r.severity == 'medium' and r.status == 'open']),
                'low': len([r for r in all_risks if r.severity == 'low' and r.status == 'open'])
            },
            'projects_with_risks': []
        }
        
        # Analyze each project
        for project in all_projects:
            analysis = self.analyze_project_risks(project.project_id)
            if analysis and (analysis['open_risks'] > 0 or analysis['warnings']):
                summary['projects_with_risks'].append(analysis)
        
        return summary
    
    def create_risk_alert(self, project_id, description, severity='medium'):
        """Create a new risk alert."""
        risk_id = self.db_manager.create_risk(project_id, description, severity, 'open')
        return risk_id
    
    def get_immediate_alerts(self):
        """Get immediate alerts that require attention."""
        alerts = []
        
        # Check for critical risks
        critical_risks = self.get_critical_risks()
        if critical_risks:
            alerts.append({
                'type': 'CRITICAL',
                'message': f"{len(critical_risks)} critical risk(s) require immediate attention!",
                'count': len(critical_risks)
            })
        
        # Check all projects for issues
        projects = self.db_manager.get_all_projects()
        for project in projects:
            analysis = self.analyze_project_risks(project.project_id)
            if analysis and analysis['warnings']:
                for warning in analysis['warnings']:
                    if 'CRITICAL' in warning:
                        alerts.append({
                            'type': 'CRITICAL',
                            'message': f"{project.name}: {warning}",
                            'project_id': project.project_id
                        })
        
        return alerts

