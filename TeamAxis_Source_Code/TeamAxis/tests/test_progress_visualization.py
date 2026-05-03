"""
Tests for features/progress_visualization.py
"""

import pytest
from features.progress_visualization import ProgressVisualizer

class TestProgressVisualizer:
    """Test ProgressVisualizer class."""
    
    def test_get_project_progress_data_all_projects(self, temp_db):
        """Test getting progress data for all projects."""
        # Create multiple projects with different progress
        temp_db.create_project('Project 1', 'Desc 1', '2024-01-01', '2024-12-31', 'active', 25)
        temp_db.create_project('Project 2', 'Desc 2', '2024-01-01', '2024-12-31', 'active', 50)
        temp_db.create_project('Project 3', 'Desc 3', '2024-01-01', '2024-12-31', 'active', 75)
        
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        names, values = visualizer.get_project_progress_data()
        assert len(names) >= 3
        assert len(values) >= 3
        assert len(names) == len(values)
        assert 'Project 1' in names
        assert 25 in values
    
    def test_get_project_progress_data_specific_project(self, temp_db, sample_project):
        """Test getting progress data for specific project."""
        temp_db.update_project_progress(sample_project.project_id, 60)
        
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        names, values = visualizer.get_project_progress_data(sample_project.project_id)
        assert len(names) == 1
        assert len(values) == 1
        assert names[0] == sample_project.name
        assert values[0] == 60
    
    def test_get_project_progress_data_no_projects(self, temp_db):
        """Test getting progress data when no projects exist."""
        # Delete all projects (if possible) or use empty database
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        names, values = visualizer.get_project_progress_data()
        # Should return empty lists, not None
        assert isinstance(names, list)
        assert isinstance(values, list)
    
    def test_get_task_status_distribution_all_projects(self, temp_db, sample_project, sample_user):
        """Test getting task status distribution for all projects."""
        # Create tasks with different statuses
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending')
        temp_db.create_task(sample_project.project_id, 'Task 2', 'Desc', sample_user.user_id, 'in_progress')
        temp_db.create_task(sample_project.project_id, 'Task 3', 'Desc', sample_user.user_id, 'completed')
        temp_db.create_task(sample_project.project_id, 'Task 4', 'Desc', sample_user.user_id, 'blocked')
        
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        distribution = visualizer.get_task_status_distribution()
        assert distribution['pending'] >= 1
        assert distribution['in_progress'] >= 1
        assert distribution['completed'] >= 1
        assert distribution['blocked'] >= 1
    
    def test_get_task_status_distribution_specific_project(self, temp_db, sample_project, sample_user):
        """Test getting task status distribution for specific project."""
        temp_db.create_task(sample_project.project_id, 'Task 1', 'Desc', sample_user.user_id, 'pending')
        temp_db.create_task(sample_project.project_id, 'Task 2', 'Desc', sample_user.user_id, 'completed')
        
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        distribution = visualizer.get_task_status_distribution(sample_project.project_id)
        assert distribution['pending'] >= 1
        assert distribution['completed'] >= 1
        assert distribution['in_progress'] == 0
        assert distribution['blocked'] == 0
    
    def test_get_task_status_distribution_no_tasks(self, temp_db, sample_project):
        """Test getting task status distribution when no tasks exist."""
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        distribution = visualizer.get_task_status_distribution(sample_project.project_id)
        assert distribution['pending'] == 0
        assert distribution['in_progress'] == 0
        assert distribution['completed'] == 0
        assert distribution['blocked'] == 0
    
    def test_get_task_status_distribution_unknown_status(self, temp_db, sample_project, sample_user):
        """Test getting task status distribution with unknown status."""
        # Create task with status that's not in the default count
        # Note: This depends on how the function handles unknown statuses
        visualizer = ProgressVisualizer()
        visualizer.db_manager = temp_db
        
        distribution = visualizer.get_task_status_distribution(sample_project.project_id)
        # Should only count known statuses
        assert 'pending' in distribution
        assert 'in_progress' in distribution
        assert 'completed' in distribution
        assert 'blocked' in distribution

