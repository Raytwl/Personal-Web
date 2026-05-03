"""
Task allocation reference module for TeamAxis.
Provides recommendations for task assignment based on workload and skills.
"""

from database.db_manager import DatabaseManager
from collections import defaultdict

class TaskAllocationManager:
    """Manages task allocation recommendations."""
    
    def __init__(self):
        """Initialize task allocation manager."""
        self.db_manager = DatabaseManager()
    
    def get_user_workload(self, user_id):
        """Calculate current workload for a user."""
        tasks = self.db_manager.get_all_tasks()
        user_tasks = [t for t in tasks if t.assignee_id == user_id]
        
        workload = {
            'total_tasks': len(user_tasks),
            'pending': sum(1 for t in user_tasks if t.status == 'pending'),
            'in_progress': sum(1 for t in user_tasks if t.status == 'in_progress'),
            'completed': sum(1 for t in user_tasks if t.status == 'completed'),
            'blocked': sum(1 for t in user_tasks if t.status == 'blocked'),
            'high_priority': sum(1 for t in user_tasks if t.priority in ['high', 'critical']),
        }
        
        # Calculate workload score (0-100)
        active_tasks = workload['pending'] + workload['in_progress']
        workload['score'] = min(100, (active_tasks * 10) + (workload['high_priority'] * 5))
        
        return workload
    
    def get_all_users_workload(self):
        """Get workload for all users."""
        users = self.db_manager.get_all_users()
        workload_data = {}
        
        for user in users:
            workload_data[user.user_id] = {
                'user': user,
                'workload': self.get_user_workload(user.user_id)
            }
        
        return workload_data
    
    def recommend_task_assignee(self, project_id, task_priority='medium'):
        """Recommend best user for task assignment based on workload."""
        users_workload = self.get_all_users_workload()
        
        # Filter users and sort by workload score (ascending)
        available_users = []
        for user_id, data in users_workload.items():
            workload_score = data['workload']['score']
            available_users.append({
                'user_id': user_id,
                'username': data['user'].username,
                'workload_score': workload_score,
                'active_tasks': data['workload']['pending'] + data['workload']['in_progress']
            })
        
        # Sort by workload score (lowest first)
        available_users.sort(key=lambda x: x['workload_score'])
        
        return available_users
    
    def get_task_allocation_summary(self, project_id=None):
        """Get summary of task allocation for a project or all projects."""
        if project_id:
            tasks = self.db_manager.get_tasks_by_project(project_id)
        else:
            tasks = self.db_manager.get_all_tasks()
        
        users = self.db_manager.get_all_users()
        user_dict = {user.user_id: user.username for user in users}
        
        allocation = defaultdict(lambda: {'total': 0, 'by_status': defaultdict(int), 'by_priority': defaultdict(int)})
        
        for task in tasks:
            if task.assignee_id:
                assignee = user_dict.get(task.assignee_id, 'Unknown')
                allocation[assignee]['total'] += 1
                allocation[assignee]['by_status'][task.status] += 1
                allocation[assignee]['by_priority'][task.priority] += 1
        
        return dict(allocation)
    
    def get_unassigned_tasks(self, project_id=None):
        """Get all unassigned tasks."""
        if project_id:
            tasks = self.db_manager.get_tasks_by_project(project_id)
        else:
            tasks = self.db_manager.get_all_tasks()
        
        return [task for task in tasks if task.assignee_id is None]
    
    def get_workload_balance_report(self):
        """Generate a workload balance report."""
        users_workload = self.get_all_users_workload()
        
        report = {
            'users': [],
            'average_workload': 0,
            'max_workload': 0,
            'min_workload': 100,
            'recommendations': []
        }
        
        total_workload = 0
        for user_id, data in users_workload.items():
            workload_score = data['workload']['score']
            total_workload += workload_score
            
            report['users'].append({
                'username': data['user'].username,
                'workload_score': workload_score,
                'active_tasks': data['workload']['pending'] + data['workload']['in_progress'],
                'total_tasks': data['workload']['total_tasks']
            })
            
            if workload_score > report['max_workload']:
                report['max_workload'] = workload_score
            if workload_score < report['min_workload']:
                report['min_workload'] = workload_score
        
        if users_workload:
            report['average_workload'] = total_workload / len(users_workload)
        
        # Generate recommendations
        if report['max_workload'] - report['min_workload'] > 30:
            report['recommendations'].append(
                "Significant workload imbalance detected. Consider redistributing tasks."
            )
        
        overloaded = [u for u in report['users'] if u['workload_score'] > 70]
        if overloaded:
            report['recommendations'].append(
                f"{len(overloaded)} user(s) are overloaded. Consider assigning new tasks to others."
            )
        
        return report

