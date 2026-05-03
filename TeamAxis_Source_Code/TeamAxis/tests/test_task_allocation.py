"""
Tests for features/task_allocation.py
"""

import pytest
from features.task_allocation import TaskAllocationManager

class TestTaskAllocationManager:
    """Test TaskAllocationManager class."""
    
    def test_get_user_workload(self, temp_db, sample_user, sample_project):
        """Test getting user workload."""
        # Create tasks for user
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending')
        temp_db.create_task(sample_project.project_id, 'Task 2', 'Desc', sample_user.user_id, 'in_progress')
        temp_db.create_task(sample_project.project_id, 'Task 3', 'Desc', sample_user.user_id, 'completed')
        temp_db.create_task(sample_project.project_id, 'Task 4', 'Desc', sample_user.user_id, 'blocked')
        temp_db.create_task(sample_project.project_id, 'Task 5', 'Desc', sample_user.user_id, 'pending', 'high')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        workload = allocation_mgr.get_user_workload(sample_user.user_id)
        assert workload['total_tasks'] >= 5
        assert workload['pending'] >= 2
        assert workload['in_progress'] >= 1
        assert workload['completed'] >= 1
        assert workload['blocked'] >= 1
        assert workload['high_priority'] >= 1
        assert 'score' in workload
        assert 0 <= workload['score'] <= 100
    
    def test_get_user_workload_no_tasks(self, temp_db, sample_user):
        """Test getting workload for user with no tasks."""
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        workload = allocation_mgr.get_user_workload(sample_user.user_id)
        assert workload['total_tasks'] == 0
        assert workload['pending'] == 0
        assert workload['score'] == 0
    
    def test_get_all_users_workload(self, temp_db, sample_user, sample_project):
        """Test getting workload for all users."""
        # Create tasks for user
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        workloads = allocation_mgr.get_all_users_workload()
        assert len(workloads) > 0
        assert sample_user.user_id in workloads
        assert 'user' in workloads[sample_user.user_id]
        assert 'workload' in workloads[sample_user.user_id]
    
    def test_recommend_task_assignee(self, temp_db, sample_user, sample_project):
        """Test recommending task assignee."""
        # Create tasks for user to increase workload
        for i in range(5):
            temp_db.create_task(sample_project.project_id, f'Task {i}', 'Desc', sample_user.user_id, 'pending')
        
        # Create another user with no tasks
        user2_id = temp_db.create_user('user2', 'pass2', 'user2@test.com', 'user')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        recommendations = allocation_mgr.recommend_task_assignee(sample_project.project_id)
        assert len(recommendations) > 0
        assert all('user_id' in r for r in recommendations)
        assert all('username' in r for r in recommendations)
        assert all('workload_score' in r for r in recommendations)
        # User with fewer tasks should have lower workload score
        user2_rec = next((r for r in recommendations if r['user_id'] == user2_id), None)
        if user2_rec:
            assert user2_rec['workload_score'] <= recommendations[0]['workload_score']
    
    def test_get_task_allocation_summary_all_projects(self, temp_db, sample_user, sample_project):
        """Test getting task allocation summary for all projects."""
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending', 'low')
        temp_db.create_task(sample_project.project_id, 'Task 2', 'Desc', sample_user.user_id, 'in_progress', 'high')
        temp_db.create_task(sample_project.project_id, 'Task 3', 'Desc', sample_user.user_id, 'completed', 'medium')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        summary = allocation_mgr.get_task_allocation_summary()
        assert isinstance(summary, dict)
        # Should have at least one user in summary
        assert len(summary) > 0
    
    def test_get_task_allocation_summary_specific_project(self, temp_db, sample_user, sample_project):
        """Test getting task allocation summary for specific project."""
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending')
        
        # Create another project and task
        project2_id = temp_db.create_project('Project 2', 'Desc', '2024-01-01', '2024-12-31')
        temp_db.create_task(project2_id, 'Task 2', 'Desc', sample_user.user_id, 'pending')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        summary = allocation_mgr.get_task_allocation_summary(sample_project.project_id)
        assert isinstance(summary, dict)
    
    def test_get_unassigned_tasks(self, temp_db, sample_project, sample_user):
        """Test getting unassigned tasks."""
        # Create assigned task
        temp_db.create_task(sample_project.project_id, 'Assigned Task', 'Desc', sample_user.user_id, 'pending')
        
        # Create unassigned tasks
        temp_db.create_task(sample_project.project_id, 'Unassigned Task 1', 'Desc', None, 'pending')
        temp_db.create_task(sample_project.project_id, 'Unassigned Task 2', 'Desc', None, 'pending')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        unassigned = allocation_mgr.get_unassigned_tasks()
        assert len(unassigned) >= 2
        assert all(t.assignee_id is None for t in unassigned)
    
    def test_get_unassigned_tasks_specific_project(self, temp_db, sample_project):
        """Test getting unassigned tasks for specific project."""
        temp_db.create_task(sample_project.project_id, 'Unassigned Task', 'Desc', None, 'pending')
        
        # Create another project with unassigned task
        project2_id = temp_db.create_project('Project 2', 'Desc', '2024-01-01', '2024-12-31')
        temp_db.create_task(project2_id, 'Other Unassigned', 'Desc', None, 'pending')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        unassigned = allocation_mgr.get_unassigned_tasks(sample_project.project_id)
        assert len(unassigned) >= 1
        assert all(t.project_id == sample_project.project_id for t in unassigned)
    
    def test_get_workload_balance_report(self, temp_db, sample_user, sample_project):
        """Test getting workload balance report."""
        # Create tasks for user
        for i in range(10):
            temp_db.create_task(sample_project.project_id, f'Task {i}', 'Desc', sample_user.user_id, 'pending')
        
        # Create another user with fewer tasks
        user2_id = temp_db.create_user('user2', 'pass2', 'user2@test.com', 'user')
        temp_db.create_task(sample_project.project_id, 'Task User2', 'Desc', user2_id, 'pending')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        report = allocation_mgr.get_workload_balance_report()
        assert 'users' in report
        assert 'average_workload' in report
        assert 'max_workload' in report
        assert 'min_workload' in report
        assert 'recommendations' in report
        assert len(report['users']) >= 2
        assert report['max_workload'] >= report['min_workload']
        assert report['max_workload'] >= report['average_workload']
    
    def test_get_workload_balance_report_imbalanced(self, temp_db, sample_user, sample_project):
        """Test workload balance report with imbalanced workload."""
        # Create many tasks for one user
        for i in range(15):
            temp_db.create_task(sample_project.project_id, f'Task {i}', 'Desc', sample_user.user_id, 'pending', 'high')
        
        # Create another user with no tasks
        user2_id = temp_db.create_user('user2', 'pass2', 'user2@test.com', 'user')
        
        allocation_mgr = TaskAllocationManager()
        allocation_mgr.db_manager = temp_db
        
        report = allocation_mgr.get_workload_balance_report()
        # Should detect imbalance
        if report['max_workload'] - report['min_workload'] > 30:
            assert len(report['recommendations']) > 0

