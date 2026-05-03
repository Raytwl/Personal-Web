"""
Project progress visualization module for TeamAxis.
"""

import matplotlib
# Suppress matplotlib warnings
matplotlib.rcParams['figure.max_open_warning'] = 0
import matplotlib.pyplot as plt
import warnings
# Suppress matplotlib warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*Tight layout.*')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from database.db_manager import DatabaseManager

class ProgressVisualizer:
    """Visualizes project progress using charts."""
    
    def __init__(self, theme_manager=None):
        """Initialize progress visualizer."""
        self.db_manager = DatabaseManager()
        self.theme_manager = theme_manager
    
    def get_project_progress_data(self, project_id=None):
        """Get progress data for visualization."""
        if project_id:
            projects = [p for p in self.db_manager.get_all_projects() if p.project_id == project_id]
        else:
            projects = self.db_manager.get_all_projects()
        
        project_names = [p.name for p in projects]
        progress_values = [p.progress for p in projects]
        
        return project_names, progress_values
    
    def get_task_status_distribution(self, project_id=None):
        """Get task status distribution for a project."""
        if project_id:
            tasks = self.db_manager.get_tasks_by_project(project_id)
        else:
            tasks = self.db_manager.get_all_tasks()
        
        status_count = {'pending': 0, 'in_progress': 0, 'completed': 0, 'blocked': 0}
        for task in tasks:
            if task.status in status_count:
                status_count[task.status] += 1
        
        return status_count
    
    def create_progress_bar_chart(self, parent_frame, project_id=None):
        """Create a progress bar chart."""
        project_names, progress_values = self.get_project_progress_data(project_id)
        
        if not project_names:
            return None
        
        # Get theme colors if available
        bg_color = self.theme_manager.get('bg_primary') if self.theme_manager else '#FFFFFF'
        fg_color = self.theme_manager.get('fg_primary') if self.theme_manager else '#000000'
        accent_color = self.theme_manager.get('accent_primary') if self.theme_manager else '#2196F3'
        
        fig, ax = plt.subplots(figsize=(8, 5), facecolor=bg_color)
        ax.set_facecolor(bg_color)
        
        bars = ax.barh(project_names, progress_values, color=accent_color)
        ax.set_xlabel('Progress (%)', fontsize=12, color=fg_color)
        ax.set_ylabel('Projects', fontsize=12, color=fg_color)
        ax.set_title('Project Progress Overview', fontsize=14, fontweight='bold', color=fg_color)
        ax.set_xlim(0, 100)
        
        # Set tick colors
        ax.tick_params(colors=fg_color)
        ax.spines['bottom'].set_color(fg_color)
        ax.spines['top'].set_color(fg_color)
        ax.spines['right'].set_color(fg_color)
        ax.spines['left'].set_color(fg_color)
        
        # Add value labels on bars
        for i, (bar, value) in enumerate(zip(bars, progress_values)):
            ax.text(value + 1, i, f'{value}%', va='center', fontsize=10, color=fg_color)
        
        # Use subplots_adjust instead of tight_layout to avoid warnings
        try:
            plt.tight_layout(pad=1.0)
        except:
            fig.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.1)
        
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        return canvas
    
    def create_task_status_pie_chart(self, parent_frame, project_id=None):
        """Create a task status pie chart."""
        status_count = self.get_task_status_distribution(project_id)
        
        if sum(status_count.values()) == 0:
            return None
        
        # Get theme colors if available
        bg_color = self.theme_manager.get('bg_primary') if self.theme_manager else '#FFFFFF'
        fg_color = self.theme_manager.get('fg_primary') if self.theme_manager else '#000000'
        
        # Use theme-aware colors for pie chart
        if self.theme_manager and self.theme_manager.is_dark():
            # Dark theme colors
            colors = [
                self.theme_manager.get('accent_danger'),    # pending - red
                self.theme_manager.get('accent_primary'),   # in_progress - blue
                self.theme_manager.get('accent_secondary'),  # completed - green
                self.theme_manager.get('accent_warning')     # blocked - orange
            ]
        else:
            # Light theme colors
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        
        labels = []
        sizes = []
        
        for status, count in status_count.items():
            if count > 0:
                labels.append(status.replace('_', ' ').title())
                sizes.append(count)
        
        if not sizes:
            return None
        
        fig, ax = plt.subplots(figsize=(7, 5), facecolor=bg_color)
        ax.set_facecolor(bg_color)
        
        # Create pie chart with theme colors
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                                         colors=colors[:len(sizes)], textprops={'color': fg_color})
        ax.set_title('Task Status Distribution', fontsize=14, fontweight='bold', color=fg_color)
        
        # Set text colors
        for text in texts:
            text.set_color(fg_color)
        for autotext in autotexts:
            autotext.set_color(fg_color)
        
        # Use subplots_adjust instead of tight_layout to avoid warnings
        try:
            plt.tight_layout(pad=1.0)
        except:
            fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        return canvas
    
    def create_progress_timeline(self, parent_frame, project_id):
        """Create a progress timeline chart."""
        project = None
        for p in self.db_manager.get_all_projects():
            if p.project_id == project_id:
                project = p
                break
        
        if not project:
            return None
        
        tasks = self.db_manager.get_tasks_by_project(project_id)
        if not tasks:
            return None
        
        # Calculate progress over time (simplified - using task completion)
        completed_tasks = sum(1 for t in tasks if t.status == 'completed')
        total_tasks = len(tasks)
        current_progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot([0, 100], [0, current_progress], marker='o', linewidth=2, markersize=8)
        ax.fill_between([0, 100], 0, current_progress, alpha=0.3)
        ax.set_xlabel('Time (%)', fontsize=12)
        ax.set_ylabel('Progress (%)', fontsize=12)
        ax.set_title(f'Progress Timeline: {project.name}', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        
        # Use subplots_adjust instead of tight_layout to avoid warnings
        try:
            plt.tight_layout(pad=1.0)
        except:
            fig.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
        
        canvas = FigureCanvasTkAgg(fig, parent_frame)
        canvas.draw()
        return canvas

