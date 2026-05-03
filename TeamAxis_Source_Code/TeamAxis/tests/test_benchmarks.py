"""
Benchmark tests for TeamAxis functions.
These tests measure the performance of critical functions to ensure they meet performance requirements.

Run benchmarks with: pytest tests/test_benchmarks.py --benchmark-only
Run with comparison: pytest tests/test_benchmarks.py --benchmark-only --benchmark-compare
"""

import pytest
import time
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from utils.helpers import (
    validate_date, validate_date_range, validate_date_reasonable,
    calculate_progress, format_date, get_status_color, get_priority_color
)
from features.task_allocation import TaskAllocationManager
from features.risk_warning import RiskWarningSystem
from features.progress_visualization import ProgressVisualizer


class TestDatabaseBenchmarks:
    """Benchmark tests for database operations."""
    
    @pytest.fixture
    def benchmark_db(self, temp_db):
        """Set up database with sample data for benchmarking."""
        db = temp_db
        
        # Create multiple users
        user_ids = []
        for i in range(50):
            user_id = db.create_user(f'user{i}', f'pass{i}', f'user{i}@test.com', 'user')
            if user_id:
                user_ids.append(user_id)
        
        # Create multiple projects
        project_ids = []
        for i in range(20):
            project_id = db.create_project(
                f'Project {i}',
                f'Description for project {i}',
                '2024-01-01',
                '2024-12-31',
                'active',
                i * 5
            )
            project_ids.append(project_id)
        
        # Create multiple tasks
        task_ids = []
        for project_id in project_ids:
            for i in range(10):
                assignee_id = user_ids[i % len(user_ids)] if user_ids else None
                task_id = db.create_task(
                    project_id,
                    f'Task {i}',
                    f'Description for task {i}',
                    assignee_id,
                    'pending' if i % 3 == 0 else 'in_progress' if i % 3 == 1 else 'completed',
                    'low' if i % 4 == 0 else 'medium' if i % 4 == 1 else 'high',
                    '2024-06-01',
                    i * 10
                )
                task_ids.append(task_id)
        
        # Create some risks
        for project_id in project_ids[:10]:
            for i in range(3):
                db.create_risk(
                    project_id,
                    f'Risk {i}',
                    'low' if i % 3 == 0 else 'medium' if i % 3 == 1 else 'high',
                    'open'
                )
        
        return db
    
    def test_hash_password_benchmark(self, benchmark):
        """Benchmark password hashing performance."""
        password = "testpassword123"
        result = benchmark(DatabaseManager.hash_password, password)
        assert result is not None
        assert len(result) == 64
    
    def test_authenticate_user_benchmark(self, benchmark, benchmark_db):
        """Benchmark user authentication performance."""
        db = benchmark_db
        result = benchmark(db.authenticate_user, 'user0', 'pass0')
        assert result is not None
    
    def test_create_user_benchmark(self, benchmark, temp_db):
        """Benchmark user creation performance."""
        db = temp_db
        
        # Use a counter to ensure unique usernames across benchmark iterations
        counter = [0]  # Use list to allow modification in closure
        
        def create_user():
            counter[0] += 1
            unique_id = int(time.time() * 1000000) + counter[0]  # Microsecond precision + counter
            return db.create_user(f'benchuser{unique_id}', 'benchpass', f'bench{unique_id}@test.com', 'user')
        
        result = benchmark(create_user)
        assert result is not None
    
    def test_get_all_users_benchmark(self, benchmark, benchmark_db):
        """Benchmark retrieving all users."""
        db = benchmark_db
        result = benchmark(db.get_all_users)
        assert len(result) > 0
    
    def test_create_project_benchmark(self, benchmark, temp_db):
        """Benchmark project creation performance."""
        db = temp_db
        
        def create_project():
            return db.create_project('Bench Project', 'Description', '2024-01-01', '2024-12-31', 'active', 0)
        
        result = benchmark(create_project)
        assert result is not None
    
    def test_get_all_projects_benchmark(self, benchmark, benchmark_db):
        """Benchmark retrieving all projects."""
        db = benchmark_db
        result = benchmark(db.get_all_projects)
        assert len(result) > 0
    
    def test_create_task_benchmark(self, benchmark, benchmark_db, sample_project, sample_user):
        """Benchmark task creation performance."""
        db = benchmark_db
        
        def create_task():
            return db.create_task(
                sample_project.project_id, 'Bench Task', 'Description', 
                sample_user.user_id, 'pending', 'medium', '2024-06-01', 0
            )
        
        result = benchmark(create_task)
        assert result is not None
    
    def test_get_all_tasks_benchmark(self, benchmark, benchmark_db):
        """Benchmark retrieving all tasks."""
        db = benchmark_db
        result = benchmark(db.get_all_tasks)
        assert len(result) > 0
    
    def test_get_tasks_by_project_benchmark(self, benchmark, benchmark_db, sample_project):
        """Benchmark retrieving tasks by project."""
        db = benchmark_db
        result = benchmark(db.get_tasks_by_project, sample_project.project_id)
        assert isinstance(result, list)
    
    def test_task_exists_in_project_benchmark(self, benchmark, benchmark_db, sample_project):
        """Benchmark task existence check."""
        db = benchmark_db
        result = benchmark(db.task_exists_in_project, sample_project.project_id, 'Task 0', '2024-06-01')
        assert isinstance(result, bool)
    
    def test_update_task_status_benchmark(self, benchmark, benchmark_db):
        """Benchmark task status update."""
        db = benchmark_db
        tasks = db.get_all_tasks()
        if tasks:
            task = tasks[0]
            benchmark(db.update_task_status, task.task_id, 'completed', 100)
    
    def test_get_all_risks_benchmark(self, benchmark, benchmark_db):
        """Benchmark retrieving all risks."""
        db = benchmark_db
        result = benchmark(db.get_all_risks)
        assert isinstance(result, list)


class TestHelperFunctionsBenchmarks:
    """Benchmark tests for helper utility functions."""
    
    def test_validate_date_valid_benchmark(self, benchmark):
        """Benchmark date validation performance for valid dates."""
        valid_date = "2024-06-15"
        result = benchmark(validate_date, valid_date)
        assert result is True
    
    def test_validate_date_invalid_benchmark(self, benchmark):
        """Benchmark date validation performance for invalid dates."""
        invalid_date = "invalid-date"
        result = benchmark(validate_date, invalid_date)
        assert result is False
    
    def test_validate_date_range_benchmark(self, benchmark):
        """Benchmark date range validation performance."""
        start = "2024-01-01"
        end = "2024-12-31"
        
        result, error = benchmark(validate_date_range, start, end)
        assert result is True
        assert error is None
    
    def test_validate_date_reasonable_valid_benchmark(self, benchmark):
        """Benchmark reasonable date validation performance for valid dates."""
        valid_date = "2024-06-15"
        result, error = benchmark(validate_date_reasonable, valid_date)
        assert result is True
    
    def test_validate_date_reasonable_invalid_benchmark(self, benchmark):
        """Benchmark reasonable date validation performance for invalid dates."""
        invalid_date = "1800-01-01"
        result, error = benchmark(validate_date_reasonable, invalid_date)
        assert result is False
    
    def test_format_date_benchmark(self, benchmark):
        """Benchmark date formatting performance."""
        date_string = "2024-06-15"
        result = benchmark(format_date, date_string)
        assert result == "2024-06-15"
    
    def test_calculate_progress_benchmark(self, benchmark):
        """Benchmark progress calculation performance."""
        result = benchmark(calculate_progress, 75, 100)
        assert result == 75
    
    def test_get_status_color_benchmark(self, benchmark):
        """Benchmark status color lookup performance."""
        result = benchmark(get_status_color, 'active')
        assert result == '#4CAF50'
    
    def test_get_priority_color_benchmark(self, benchmark):
        """Benchmark priority color lookup performance."""
        result = benchmark(get_priority_color, 'high')
        assert result == '#FF5722'


class TestTaskAllocationBenchmarks:
    """Benchmark tests for task allocation functions."""
    
    @pytest.fixture
    def allocation_manager(self, temp_db):
        """Create TaskAllocationManager with sample data."""
        manager = TaskAllocationManager()
        manager.db_manager = temp_db
        
        # Create users
        user_ids = []
        for i in range(20):
            user_id = temp_db.create_user(f'user{i}', f'pass{i}', f'user{i}@test.com', 'user')
            if user_id:
                user_ids.append(user_id)
        
        # Create project
        project_id = temp_db.create_project(
            'Test Project',
            'Description',
            '2024-01-01',
            '2024-12-31',
            'active',
            0
        )
        
        # Create tasks with various assignments
        for i in range(100):
            assignee_id = user_ids[i % len(user_ids)] if user_ids else None
            temp_db.create_task(
                project_id,
                f'Task {i}',
                f'Description {i}',
                assignee_id,
                'pending' if i % 3 == 0 else 'in_progress' if i % 3 == 1 else 'completed',
                'low' if i % 4 == 0 else 'medium' if i % 4 == 1 else 'high',
                '2024-06-01',
                i * 10
            )
        
        return manager, project_id
    
    def test_get_user_workload_benchmark(self, benchmark, allocation_manager):
        """Benchmark user workload calculation."""
        manager, project_id = allocation_manager
        users = manager.db_manager.get_all_users()
        if users:
            user_id = users[0].user_id
            result = benchmark(manager.get_user_workload, user_id)
            assert 'total_tasks' in result
            assert 'score' in result
    
    def test_get_all_users_workload_benchmark(self, benchmark, allocation_manager):
        """Benchmark getting workload for all users."""
        manager, project_id = allocation_manager
        result = benchmark(manager.get_all_users_workload)
        assert isinstance(result, dict)
        assert len(result) > 0
    
    def test_recommend_task_assignee_benchmark(self, benchmark, allocation_manager):
        """Benchmark task assignee recommendation."""
        manager, project_id = allocation_manager
        result = benchmark(manager.recommend_task_assignee, project_id, 'medium')
        assert isinstance(result, list)
        assert len(result) > 0
    
    def test_get_task_allocation_summary_benchmark(self, benchmark, allocation_manager):
        """Benchmark task allocation summary generation."""
        manager, project_id = allocation_manager
        result = benchmark(manager.get_task_allocation_summary, project_id)
        assert isinstance(result, dict)
    
    def test_get_workload_balance_report_benchmark(self, benchmark, allocation_manager):
        """Benchmark workload balance report generation."""
        manager, project_id = allocation_manager
        result = benchmark(manager.get_workload_balance_report)
        assert isinstance(result, dict)
        assert 'users' in result
        assert 'average_workload' in result


class TestRiskWarningBenchmarks:
    """Benchmark tests for risk warning system functions."""
    
    @pytest.fixture
    def risk_system(self, temp_db):
        """Create RiskWarningSystem with sample data."""
        system = RiskWarningSystem()
        system.db_manager = temp_db
        
        # Create projects
        project_ids = []
        for i in range(10):
            project_id = temp_db.create_project(
                f'Project {i}',
                f'Description {i}',
                '2024-01-01',
                '2024-12-31',
                'active',
                i * 10
            )
            project_ids.append(project_id)
        
        # Create risks
        for project_id in project_ids:
            for i in range(5):
                temp_db.create_risk(
                    project_id,
                    f'Risk {i}',
                    'low' if i % 4 == 0 else 'medium' if i % 4 == 1 else 'high',
                    'open' if i % 2 == 0 else 'closed'
                )
        
        # Create tasks for risk analysis
        for project_id in project_ids:
            for i in range(10):
                temp_db.create_task(
                    project_id,
                    f'Task {i}',
                    f'Description {i}',
                    None,
                    'pending' if i % 3 == 0 else 'in_progress' if i % 3 == 1 else 'completed',
                    'medium',
                    '2024-06-01',
                    i * 10
                )
        
        return system, project_ids[0]
    
    def test_get_all_risks_benchmark(self, benchmark, risk_system):
        """Benchmark retrieving all risks."""
        system, project_id = risk_system
        result = benchmark(system.get_all_risks)
        assert isinstance(result, list)
    
    def test_get_critical_risks_benchmark(self, benchmark, risk_system):
        """Benchmark retrieving critical risks."""
        system, project_id = risk_system
        result = benchmark(system.get_critical_risks)
        assert isinstance(result, list)
    
    def test_get_open_risks_benchmark(self, benchmark, risk_system):
        """Benchmark retrieving open risks."""
        system, project_id = risk_system
        result = benchmark(system.get_open_risks)
        assert isinstance(result, list)
    
    def test_analyze_project_risks_benchmark(self, benchmark, risk_system):
        """Benchmark project risk analysis."""
        system, project_id = risk_system
        result = benchmark(system.analyze_project_risks, project_id)
        assert result is not None
        assert 'total_risks' in result
        assert 'warnings' in result
    
    def test_get_risk_summary_benchmark(self, benchmark, risk_system):
        """Benchmark risk summary generation."""
        system, project_id = risk_system
        result = benchmark(system.get_risk_summary)
        assert isinstance(result, dict)
        assert 'total_risks' in result
        assert 'by_severity' in result
    
    def test_get_immediate_alerts_benchmark(self, benchmark, risk_system):
        """Benchmark immediate alerts generation."""
        system, project_id = risk_system
        result = benchmark(system.get_immediate_alerts)
        assert isinstance(result, list)


class TestProgressVisualizationBenchmarks:
    """Benchmark tests for progress visualization functions."""
    
    @pytest.fixture
    def visualizer(self, temp_db):
        """Create ProgressVisualizer with sample data."""
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        # Create projects
        project_ids = []
        for i in range(15):
            project_id = temp_db.create_project(
                f'Project {i}',
                f'Description {i}',
                '2024-01-01',
                '2024-12-31',
                'active',
                i * 5
            )
            project_ids.append(project_id)
        
        # Create tasks
        for project_id in project_ids:
            for i in range(20):
                temp_db.create_task(
                    project_id,
                    f'Task {i}',
                    f'Description {i}',
                    None,
                    'pending' if i % 3 == 0 else 'in_progress' if i % 3 == 1 else 'completed',
                    'medium',
                    '2024-06-01',
                    i * 5
                )
        
        return visualizer, project_ids[0]
    
    def test_get_project_progress_data_benchmark(self, benchmark, visualizer):
        """Benchmark getting project progress data."""
        viz, project_id = visualizer
        result = benchmark(viz.get_project_progress_data)
        project_names, progress_values = result
        assert len(project_names) > 0
        assert len(progress_values) > 0
    
    def test_get_project_progress_data_by_id_benchmark(self, benchmark, visualizer):
        """Benchmark getting project progress data for specific project."""
        viz, project_id = visualizer
        result = benchmark(viz.get_project_progress_data, project_id)
        project_names, progress_values = result
        assert len(project_names) > 0
    
    def test_get_task_status_distribution_benchmark(self, benchmark, visualizer):
        """Benchmark getting task status distribution."""
        viz, project_id = visualizer
        result = benchmark(viz.get_task_status_distribution)
        assert isinstance(result, dict)
        assert 'pending' in result
        assert 'completed' in result
    
    def test_get_task_status_distribution_by_project_benchmark(self, benchmark, visualizer):
        """Benchmark getting task status distribution for specific project."""
        viz, project_id = visualizer
        result = benchmark(viz.get_task_status_distribution, project_id)
        assert isinstance(result, dict)


class TestBulkOperationsBenchmarks:
    """Benchmark tests for bulk operations and scalability."""
    
    def test_bulk_user_creation_benchmark(self, benchmark, temp_db):
        """Benchmark creating multiple users in sequence."""
        db = temp_db
        
        # Use a counter to ensure unique usernames across benchmark iterations
        counter = [0]  # Use list to allow modification in closure
        
        def create_users():
            counter[0] += 1
            base_id = int(time.time() * 1000000) + counter[0] * 100000  # Unique base for this iteration
            user_ids = []
            for i in range(100):
                unique_id = base_id + i
                user_id = db.create_user(f'bulkuser{unique_id}', f'pass{i}', f'bulkuser{unique_id}@test.com', 'user')
                if user_id:
                    user_ids.append(user_id)
            return user_ids
        
        result = benchmark(create_users)
        assert len(result) == 100, f"Expected 100 users, got {len(result)}"
    
    def test_bulk_task_creation_benchmark(self, benchmark, temp_db, sample_project, sample_user):
        """Benchmark creating multiple tasks in sequence."""
        db = temp_db
        
        def create_tasks():
            task_ids = []
            for i in range(200):
                task_id = db.create_task(
                    sample_project.project_id,
                    f'Bulk Task {i}',
                    f'Description {i}',
                    sample_user.user_id,
                    'pending',
                    'medium',
                    '2024-06-01',
                    0
                )
                task_ids.append(task_id)
            return task_ids
        
        result = benchmark(create_tasks)
        assert len(result) == 200
    
    def test_large_dataset_query_all_tasks_benchmark(self, benchmark, temp_db):
        """Benchmark querying all tasks from large datasets."""
        db = temp_db
        
        # Create large dataset
        project_id = db.create_project('Large Project', 'Description', '2024-01-01', '2024-12-31', 'active', 0)
        user_id = db.create_user('testuser', 'testpass', 'test@test.com', 'user')
        
        # Create 500 tasks
        for i in range(500):
            db.create_task(
                project_id,
                f'Task {i}',
                f'Description {i}',
                user_id,
                'pending' if i % 3 == 0 else 'in_progress' if i % 3 == 1 else 'completed',
                'medium',
                '2024-06-01',
                i * 2
            )
        
        # Benchmark querying all tasks
        result = benchmark(db.get_all_tasks)
        assert len(result) == 500
    
    def test_large_dataset_query_by_project_benchmark(self, benchmark, temp_db):
        """Benchmark querying tasks by project from large datasets."""
        db = temp_db
        
        # Create large dataset
        project_id = db.create_project('Large Project 2', 'Description', '2024-01-01', '2024-12-31', 'active', 0)
        user_id = db.create_user('testuser2', 'testpass', 'test2@test.com', 'user')
        
        # Create 500 tasks
        for i in range(500):
            db.create_task(
                project_id,
                f'Task {i}',
                f'Description {i}',
                user_id,
                'pending' if i % 3 == 0 else 'in_progress' if i % 3 == 1 else 'completed',
                'medium',
                '2024-06-01',
                i * 2
            )
        
        # Benchmark querying tasks by project
        result = benchmark(db.get_tasks_by_project, project_id)
        assert len(result) == 500

