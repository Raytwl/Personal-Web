"""
Main window for TeamAxis project management system.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import os
from database.db_manager import DatabaseManager
from license.license_manager import LicenseManager
from features.progress_visualization import ProgressVisualizer
from features.task_allocation import TaskAllocationManager
from features.risk_warning import RiskWarningSystem
from utils.helpers import format_date, get_status_color, get_priority_color, get_severity_color, validate_date, validate_date_range, validate_date_reasonable
from utils.language_manager import get_language_manager
from utils.theme_manager import get_theme_manager

class MainWindow:
    """Main application window."""
    
    def __init__(self, auth_manager):
        """Initialize main window."""
        self.auth_manager = auth_manager
        self.db_manager = DatabaseManager()
        self.license_manager = LicenseManager()
        self.lang = get_language_manager()
        self.theme = get_theme_manager()
        self.progress_visualizer = ProgressVisualizer(self.theme)
        self.task_allocation = TaskAllocationManager()
        self.risk_warning = RiskWarningSystem()
        
        self.window = tk.Tk()
        self.window.title(self.lang.t('app_title'))
        self.window.geometry("1200x800")
        self.set_window_icon()
        self.apply_theme()
        # Try to maximize window (Windows uses 'zoomed', Linux/Mac use different methods)
        try:
            self.window.state('zoomed')  # Windows
        except:
            try:
                self.window.attributes('-zoomed', True)  # Linux
            except:
                self.window.state('normal')  # Fallback
        
        self.create_menu()
        self.create_main_interface()
        self.check_risk_alerts()
    
    def create_menu(self):
        """Create menu bar."""
        self.menubar = tk.Menu(self.window)
        self.window.config(menu=self.menubar)
        self.update_menu()
    
    def update_menu(self):
        """Update menu with current language."""
        # Clear existing menu
        self.menubar.delete(0, tk.END)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.lang.t('menu_file'), menu=file_menu)
        file_menu.add_command(label=self.lang.t('menu_logout'), command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label=self.lang.t('menu_exit'), command=self.window.quit)
        
        # Projects menu
        projects_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.lang.t('menu_projects'), menu=projects_menu)
        projects_menu.add_command(label=self.lang.t('menu_new_project'), command=self.show_new_project_dialog)
        projects_menu.add_command(label=self.lang.t('menu_view_all_projects'), command=self.refresh_projects)
        
        # Tasks menu
        tasks_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.lang.t('menu_tasks'), menu=tasks_menu)
        tasks_menu.add_command(label=self.lang.t('menu_new_task'), command=self.show_new_task_dialog)
        tasks_menu.add_command(label=self.lang.t('menu_view_all_tasks'), command=self.refresh_tasks)
        
        # License menu
        license_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.lang.t('menu_license'), menu=license_menu)
        license_menu.add_command(label=self.lang.t('menu_manage_licenses'), command=self.show_license_management)
        
        # Features menu
        features_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.lang.t('menu_features'), menu=features_menu)
        features_menu.add_command(label=self.lang.t('menu_progress_visualization'), command=self.show_progress_visualization)
        features_menu.add_command(label=self.lang.t('menu_task_allocation'), command=self.show_task_allocation)
        features_menu.add_command(label=self.lang.t('menu_risk_warning'), command=self.show_risk_warning)
        
        # Language menu
        language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.lang.t('menu_language'), menu=language_menu)
        language_menu.add_command(label=self.lang.t('menu_english'), command=lambda: self.change_language('en'))
        language_menu.add_command(label=self.lang.t('menu_traditional_chinese'), command=lambda: self.change_language('zh_TW'))
        
        # Theme menu
        theme_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.lang.t('menu_theme'), menu=theme_menu)
        theme_menu.add_command(label=self.lang.t('menu_light_theme'), command=lambda: self.change_theme('light'))
        theme_menu.add_command(label=self.lang.t('menu_dark_theme'), command=lambda: self.change_theme('dark'))
    
    def change_language(self, language):
        """Change application language."""
        if self.lang.set_language(language):
            self.window.title(self.lang.t('app_title'))
            # Recreate menu
            self.update_menu()
            # Recreate all tabs with new language
            self.recreate_interface()
            # Refresh charts if on visualization tab
            if hasattr(self, 'notebook') and self.notebook:
                try:
                    current_tab = self.notebook.index(self.notebook.select())
                    # Visualization tab is index 4
                    if current_tab == 4:
                        self.update_visualization()
                except:
                    pass
            messagebox.showinfo(self.lang.t('success'), f"Language changed to {self.lang.t('menu_english' if language == 'en' else 'menu_traditional_chinese')}")
    
    def recreate_interface(self):
        """Recreate interface with new language/theme."""
        # Get currently selected tab index before destroying
        selected_tab = 0
        if hasattr(self, 'notebook') and self.notebook:
            try:
                selected_tab = self.notebook.index(self.notebook.select())
            except:
                selected_tab = 0
        
        # Destroy existing container frame (which includes notebook and logo)
        if hasattr(self, 'header_frame'):
            self.header_frame.destroy()
        if hasattr(self, 'container_frame'):
            self.container_frame.destroy()
        
        # Recreate interface
        self.create_main_interface()
        
        # Restore the previously selected tab
        try:
            self.notebook.select(selected_tab)
        except:
            # If tab index is invalid, select first tab
            self.notebook.select(0)
    
    def load_logo(self, size=(50, 50)):
        """Load logo image from file, theme-aware."""
        import os
        # Get script directory and project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up from ui/ to project root
        cwd = os.getcwd()
        
        # Try theme-specific logos first
        is_dark = self.theme.is_dark()
        
        if is_dark:
            # Dark theme - try dark logo variants first
            logo_paths = [
                'logo_dark.png', 'teamaxis_logo_dark.png',
                'assets/logo_dark.png', 'assets/teamaxis_logo_dark.png',
                'logo.png', 'teamaxis_logo.png',
                'assets/logo.png', 'assets/teamaxis_logo.png'
            ]
        else:
            # Light theme - try light logo variants first
            logo_paths = [
                'logo_light.png', 'teamaxis_logo_light.png',
                'assets/logo_light.png', 'assets/teamaxis_logo_light.png',
                'logo.png', 'teamaxis_logo.png',
                'assets/logo.png', 'assets/teamaxis_logo.png'
            ]
        
        print(f"Loading logo (theme: {'dark' if is_dark else 'light'}, cwd: {cwd}, project_root: {project_root})")
        for path in logo_paths:
            # Try multiple locations: relative to cwd, relative to project root, and relative to script dir
            possible_paths = [
                path,  # Try relative to current working directory
                os.path.join(cwd, path),  # Try relative to cwd
                os.path.join(project_root, path),  # Try relative to project root
                os.path.join(script_dir, path),  # Try relative to script directory
            ]
            
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    try:
                        img = Image.open(file_path)
                        img = img.resize(size, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        print(f"Logo loaded successfully from: {file_path}")
                        return photo
                    except Exception as e:
                        print(f"Error loading logo from {file_path}: {e}")
                        import traceback
                        traceback.print_exc()
        
        print(f"Logo not found after checking all paths.")
        return None
    
    def set_window_icon(self):
        """Set the window icon using the light-themed logo."""
        # Always use light-themed logo for window icon
        icon_image = self.load_light_logo(size=(32, 32))
        if icon_image:
            try:
                self.window.iconphoto(True, icon_image)
            except Exception as e:
                print(f"Error setting window icon: {e}")
    
    def load_light_logo(self, size=(32, 32)):
        """Load light-themed logo image from file."""
        import os
        # Get script directory and project root
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # Go up from ui/ to project root
        cwd = os.getcwd()
        
        # Always use light logo variants
        logo_paths = [
            'logo_light.png', 'teamaxis_logo_light.png',
            'assets/logo_light.png', 'assets/teamaxis_logo_light.png',
            'logo.png', 'teamaxis_logo.png',
            'assets/logo.png', 'assets/teamaxis_logo.png'
        ]
        
        for path in logo_paths:
            # Try multiple locations: relative to cwd, relative to project root, and relative to script dir
            possible_paths = [
                path,  # Try relative to current working directory
                os.path.join(cwd, path),  # Try relative to cwd
                os.path.join(project_root, path),  # Try relative to project root
                os.path.join(script_dir, path),  # Try relative to script directory
            ]
            
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    try:
                        img = Image.open(file_path)
                        img = img.resize(size, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        return photo
                    except Exception as e:
                        print(f"Error loading light logo from {file_path}: {e}")
        
        return None
    
    def apply_theme(self):
        """Apply current theme to window and configure ttk styles."""
        self.window.configure(bg=self.theme.get('bg_primary'))
        
        # Configure ttk styles for theme
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure Treeview style
        style.configure('Treeview',
                       background=self.theme.get('tree_bg'),
                       foreground=self.theme.get('tree_fg'),
                       fieldbackground=self.theme.get('tree_bg'),
                       borderwidth=1)
        style.map('Treeview',
                 background=[('selected', self.theme.get('tree_select'))],
                 foreground=[('selected', self.theme.get('tree_fg'))])
        
        # Configure Notebook style
        style.configure('TNotebook',
                       background=self.theme.get('bg_primary'),
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=self.theme.get('bg_secondary'),
                       foreground=self.theme.get('fg_primary'),
                       padding=[12, 8])
        style.map('TNotebook.Tab',
                 background=[('selected', self.theme.get('bg_primary'))],
                 expand=[('selected', [1, 1, 1, 0])])
        
        # Configure Combobox style
        style.configure('TCombobox',
                       fieldbackground=self.theme.get('entry_bg'),
                       background=self.theme.get('entry_bg'),
                       foreground=self.theme.get('entry_fg'),
                       borderwidth=1)
        
        # Configure Scrollbar style
        style.configure('TScrollbar',
                       background=self.theme.get('bg_secondary'),
                       troughcolor=self.theme.get('bg_primary'),
                       borderwidth=0,
                       arrowcolor=self.theme.get('fg_primary'),
                       darkcolor=self.theme.get('bg_secondary'),
                       lightcolor=self.theme.get('bg_secondary'))
    
    def change_theme(self, theme):
        """Change application theme."""
        if self.theme.set_theme(theme):
            # Update progress visualizer theme
            self.progress_visualizer.theme_manager = self.theme
            self.apply_theme()
            # Recreate interface to apply theme colors
            self.recreate_interface()
            # Refresh charts if on visualization tab
            if hasattr(self, 'notebook') and self.notebook:
                try:
                    current_tab = self.notebook.index(self.notebook.select())
                    # Visualization tab is index 4
                    if current_tab == 4:
                        self.update_visualization()
                except:
                    pass
            messagebox.showinfo(self.lang.t('success'), f"Theme changed to {self.theme.get_theme_name()}")
    
    def create_main_interface(self):
        """Create main interface with notebook tabs."""
        # Create container frame for notebook and logo
        self.container_frame = tk.Frame(self.window, bg=self.theme.get('bg_primary'))
        self.container_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.container_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Load logo and position it to align with tabs
        self.logo_image = self.load_logo(size=(60, 60))
        if self.logo_image:
            # Create a frame for the logo positioned to align with tabs
            # Tabs typically have padding of [12, 8], so we position logo at y=8 to align with tab text
            self.logo_label = tk.Label(self.container_frame, image=self.logo_image, bg=self.theme.get('bg_primary'))
            self.logo_label.image = self.logo_image  # Keep a reference
            # Position logo in top-right, aligned with tab bar (approximately 8-10px from top)
            self.logo_label.place(relx=1.0, x=-15, y=10, anchor=tk.NE)
            print(f"Logo loaded and displayed aligned with tabs. Theme: {self.theme.current_theme}")
        else:
            print("Warning: Logo image not loaded. Check if logo files exist in assets folder.")
        
        # Dashboard tab
        self.create_dashboard_tab()
        
        # Projects tab
        self.create_projects_tab()
        
        # Tasks tab
        self.create_tasks_tab()
        
        # License Management tab
        self.create_license_tab()
        
        # Progress Visualization tab
        self.create_visualization_tab()
        
        # Task Allocation tab
        self.create_allocation_tab()
        
        # Risk Warning tab
        self.create_risk_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab."""
        dashboard_frame = tk.Frame(self.notebook, bg=self.theme.get('bg_primary'))
        self.notebook.add(dashboard_frame, text=self.lang.t('dashboard'))
        
        # Welcome message
        welcome_label = tk.Label(
            dashboard_frame,
            text=self.lang.t('welcome', username=self.auth_manager.get_current_user().username),
            font=("Arial", 18, "bold"),
            bg=self.theme.get('bg_primary'),
            fg=self.theme.get('fg_primary'),
            pady=20
        )
        welcome_label.pack()
        
        # Statistics frame
        stats_frame = tk.Frame(dashboard_frame, bg=self.theme.get('bg_primary'))
        stats_frame.pack(pady=20)
        
        projects = self.db_manager.get_all_projects()
        tasks = self.db_manager.get_all_tasks()
        risks = self.risk_warning.get_all_risks()
        open_risks = self.risk_warning.get_open_risks()
        
        stats = [
            (self.lang.t('total_projects'), len(projects), "#2196F3"),
            (self.lang.t('total_tasks'), len(tasks), "#4CAF50"),
            (self.lang.t('open_risks'), len(open_risks), "#FF5722"),
            (self.lang.t('active_projects'), len([p for p in projects if p.status == 'active']), "#FF9800")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, relief=tk.RAISED, borderwidth=2, bg=self.theme.get('bg_secondary'))
            stat_frame.grid(row=0, column=i, padx=10, pady=10)
            
            value_label = tk.Label(
                stat_frame,
                text=str(value),
                font=("Arial", 24, "bold"),
                fg=color,
                bg=self.theme.get('bg_secondary'),
                pady=10,
                padx=20
            )
            value_label.pack()
            
            label_label = tk.Label(
                stat_frame,
                text=label,
                font=("Arial", 10),
                bg=self.theme.get('bg_secondary'),
                fg=self.theme.get('fg_primary'),
                pady=5
            )
            label_label.pack()
        
        # Recent projects
        recent_frame = tk.LabelFrame(
            dashboard_frame, 
            text=self.lang.t('recent_projects'), 
            padx=10, 
            pady=10,
            bg=self.theme.get('bg_primary'),
            fg=self.theme.get('fg_primary')
        )
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.recent_projects_tree = ttk.Treeview(
            recent_frame,
            columns=("Name", "Status", "Progress"),
            show="headings",
            height=10
        )
        self.recent_projects_tree.heading("Name", text=self.lang.t('project_name'))
        self.recent_projects_tree.heading("Status", text=self.lang.t('status'))
        self.recent_projects_tree.heading("Progress", text=self.lang.t('progress'))
        self.recent_projects_tree.column("Name", width=300)
        self.recent_projects_tree.column("Status", width=100)
        self.recent_projects_tree.column("Progress", width=100)
        self.recent_projects_tree.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_dashboard()
    
    def create_projects_tab(self):
        """Create projects management tab."""
        projects_frame = tk.Frame(self.notebook, bg=self.theme.get('bg_primary'))
        self.notebook.add(projects_frame, text=self.lang.t('projects'))
        
        # Toolbar
        toolbar = tk.Frame(projects_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(toolbar, text=self.lang.t('new_project'), command=self.show_new_project_dialog, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('delete_project'), command=self.delete_selected_project, bg="#F44336", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('refresh'), command=self.refresh_projects, bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=5)
        
        # Projects tree
        tree_frame = tk.Frame(projects_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.projects_tree = ttk.Treeview(
            tree_frame,
            columns=("Name", "Description", "Start Date", "End Date", "Status", "Progress"),
            show="headings",
            height=20
        )
        
        self.projects_tree.heading("Name", text=self.lang.t('project_name'))
        self.projects_tree.heading("Description", text=self.lang.t('description'))
        self.projects_tree.heading("Start Date", text=self.lang.t('start_date'))
        self.projects_tree.heading("End Date", text=self.lang.t('end_date'))
        self.projects_tree.heading("Status", text=self.lang.t('status'))
        self.projects_tree.heading("Progress", text=self.lang.t('progress'))
        
        self.projects_tree.column("Name", width=200)
        self.projects_tree.column("Description", width=300)
        self.projects_tree.column("Start Date", width=100)
        self.projects_tree.column("End Date", width=100)
        self.projects_tree.column("Status", width=100)
        self.projects_tree.column("Progress", width=100)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.projects_tree.yview)
        self.projects_tree.configure(yscrollcommand=scrollbar.set)
        
        self.projects_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.projects_tree.bind("<Double-1>", self.on_project_select)
        
        self.refresh_projects()
    
    def create_tasks_tab(self):
        """Create tasks management tab."""
        tasks_frame = tk.Frame(self.notebook, bg=self.theme.get('bg_primary'))
        self.notebook.add(tasks_frame, text=self.lang.t('tasks'))
        
        # Toolbar
        toolbar = tk.Frame(tasks_frame, bg=self.theme.get('bg_primary'))
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(toolbar, text=self.lang.t('new_task'), command=self.show_new_task_dialog, bg=self.theme.get('accent_secondary'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('edit_task'), command=self.show_edit_task_dialog, bg=self.theme.get('accent_warning'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('mark_as_complete'), command=self.mark_task_complete, bg=self.theme.get('accent_secondary'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('delete_task'), command=self.delete_selected_task, bg=self.theme.get('accent_danger'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('refresh'), command=self.refresh_tasks, bg=self.theme.get('accent_primary'), fg="white").pack(side=tk.LEFT, padx=5)
        
        # Tasks tree
        tree_frame = tk.Frame(tasks_frame, bg=self.theme.get('bg_primary'))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tasks_tree = ttk.Treeview(
            tree_frame,
            columns=("Project", "Name", "Assignee", "Status", "Priority", "Due Date", "Progress"),
            show="headings",
            height=20
        )
        
        self.tasks_tree.heading("Project", text=self.lang.t('project'))
        self.tasks_tree.heading("Name", text=self.lang.t('task_name'))
        self.tasks_tree.heading("Assignee", text=self.lang.t('assignee'))
        self.tasks_tree.heading("Status", text=self.lang.t('status'))
        self.tasks_tree.heading("Priority", text=self.lang.t('priority'))
        self.tasks_tree.heading("Due Date", text=self.lang.t('due_date'))
        self.tasks_tree.heading("Progress", text=self.lang.t('progress'))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tasks_tree.yview)
        self.tasks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.tasks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_tasks()
    
    def create_license_tab(self):
        """Create license management tab."""
        license_frame = tk.Frame(self.notebook, bg=self.theme.get('bg_primary'))
        self.notebook.add(license_frame, text=self.lang.t('license_management'))
        
        # Toolbar
        toolbar = tk.Frame(license_frame, bg=self.theme.get('bg_primary'))
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Only show generate license button for admin users
        if self.auth_manager.is_admin():
            tk.Button(toolbar, text=self.lang.t('generate_license'), command=self.show_generate_license_dialog, bg=self.theme.get('accent_secondary'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('refresh'), command=self.refresh_licenses, bg=self.theme.get('accent_primary'), fg="white").pack(side=tk.LEFT, padx=5)
        
        # Licenses tree
        tree_frame = tk.Frame(license_frame, bg=self.theme.get('bg_primary'))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # For normal users, hide the "User" column since they only see their own license
        is_admin = self.auth_manager.is_admin()
        if is_admin:
            columns = ("License Key", "User", "Issue Date", "Expiry Date", "Status")
        else:
            columns = ("License Key", "Issue Date", "Expiry Date", "Status")
        
        self.licenses_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            height=20
        )
        
        self.licenses_tree.heading("License Key", text=self.lang.t('license_key_col'))
        if is_admin:
            self.licenses_tree.heading("User", text=self.lang.t('user'))
        self.licenses_tree.heading("Issue Date", text=self.lang.t('issue_date'))
        self.licenses_tree.heading("Expiry Date", text=self.lang.t('expiry_date'))
        self.licenses_tree.heading("Status", text=self.lang.t('status'))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.licenses_tree.yview)
        self.licenses_tree.configure(yscrollcommand=scrollbar.set)
        
        self.licenses_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_licenses()
    
    def create_visualization_tab(self):
        """Create progress visualization tab."""
        viz_frame = tk.Frame(self.notebook, bg=self.theme.get('bg_primary'))
        self.notebook.add(viz_frame, text=self.lang.t('progress_visualization'))
        
        # Control frame
        control_frame = tk.Frame(viz_frame, bg=self.theme.get('bg_primary'))
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Label(control_frame, text=self.lang.t('select_project'), bg=self.theme.get('bg_primary'), fg=self.theme.get('fg_primary')).pack(side=tk.LEFT, padx=5)
        self.viz_project_var = tk.StringVar()
        self.viz_project_combo = ttk.Combobox(control_frame, textvariable=self.viz_project_var, state="readonly", width=30)
        self.viz_project_combo.pack(side=tk.LEFT, padx=5)
        self.viz_project_combo.bind("<<ComboboxSelected>>", self.update_visualization)
        
        tk.Button(control_frame, text=self.lang.t('refresh_charts'), command=self.update_visualization, bg=self.theme.get('accent_primary'), fg="white").pack(side=tk.LEFT, padx=5)
        
        # Charts frame - use grid for side-by-side layout
        charts_frame = tk.Frame(viz_frame, bg=self.theme.get('bg_primary'))
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Progress bar chart - left side
        self.progress_chart_frame = tk.Frame(charts_frame)
        self.progress_chart_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Task status pie chart - right side
        self.task_chart_frame = tk.Frame(charts_frame)
        self.task_chart_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        self.update_project_combo()
        self.update_visualization()
    
    def create_allocation_tab(self):
        """Create task allocation tab."""
        alloc_frame = tk.Frame(self.notebook, bg=self.theme.get('bg_primary'))
        self.notebook.add(alloc_frame, text=self.lang.t('task_allocation'))
        
        # Toolbar
        toolbar = tk.Frame(alloc_frame, bg=self.theme.get('bg_primary'))
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(toolbar, text="Refresh", command=self.refresh_allocation, bg=self.theme.get('accent_primary'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Workload Report", command=self.show_workload_report, bg=self.theme.get('accent_secondary'), fg="white").pack(side=tk.LEFT, padx=5)
        
        # Allocation tree
        tree_frame = tk.Frame(alloc_frame, bg=self.theme.get('bg_primary'))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.allocation_tree = ttk.Treeview(
            tree_frame,
            columns=("User", "Total Tasks", "Pending", "In Progress", "Completed", "Workload Score"),
            show="headings",
            height=20
        )
        
        self.allocation_tree.heading("User", text="User")
        self.allocation_tree.heading("Total Tasks", text="Total Tasks")
        self.allocation_tree.heading("Pending", text="Pending")
        self.allocation_tree.heading("In Progress", text="In Progress")
        self.allocation_tree.heading("Completed", text="Completed")
        self.allocation_tree.heading("Workload Score", text="Workload Score")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.allocation_tree.yview)
        self.allocation_tree.configure(yscrollcommand=scrollbar.set)
        
        self.allocation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_allocation()
    
    def create_risk_tab(self):
        """Create risk warning tab."""
        risk_frame = tk.Frame(self.notebook, bg=self.theme.get('bg_primary'))
        self.notebook.add(risk_frame, text=self.lang.t('risk_warning'))
        
        # Toolbar
        toolbar = tk.Frame(risk_frame, bg=self.theme.get('bg_primary'))
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(toolbar, text=self.lang.t('add_risk'), command=self.show_add_risk_dialog, bg=self.theme.get('accent_secondary'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('refresh'), command=self.refresh_risks, bg=self.theme.get('accent_primary'), fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text=self.lang.t('risk_summary'), command=self.show_risk_summary, bg=self.theme.get('accent_warning'), fg="white").pack(side=tk.LEFT, padx=5)
        
        # Risks tree
        tree_frame = tk.Frame(risk_frame, bg=self.theme.get('bg_primary'))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.risks_tree = ttk.Treeview(
            tree_frame,
            columns=("Project", "Description", "Severity", "Status", "Mitigation"),
            show="headings",
            height=20
        )
        
        self.risks_tree.heading("Project", text=self.lang.t('project'))
        self.risks_tree.heading("Description", text=self.lang.t('description'))
        self.risks_tree.heading("Severity", text=self.lang.t('severity'))
        self.risks_tree.heading("Status", text=self.lang.t('status'))
        self.risks_tree.heading("Mitigation", text=self.lang.t('mitigation'))
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.risks_tree.yview)
        self.risks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.risks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_risks()
    
    # Refresh methods
    def refresh_dashboard(self):
        """Refresh dashboard data."""
        # Check if recent_projects_tree exists
        if not hasattr(self, 'recent_projects_tree') or self.recent_projects_tree is None:
            return
        
        for item in self.recent_projects_tree.get_children():
            self.recent_projects_tree.delete(item)
        
        projects = self.db_manager.get_all_projects()[:10]  # Show last 10
        for project in projects:
            self.recent_projects_tree.insert("", tk.END, values=(
                project.name, project.status, f"{project.progress}%"
            ))
    
    def refresh_projects(self):
        """Refresh projects list and switch to Projects tab."""
        # Switch to Projects tab (index 1: Dashboard=0, Projects=1, Tasks=2, ...)
        if hasattr(self, 'notebook') and self.notebook is not None:
            self.notebook.select(1)
        
        # Check if projects_tree exists
        if not hasattr(self, 'projects_tree') or self.projects_tree is None:
            return
        
        for item in self.projects_tree.get_children():
            self.projects_tree.delete(item)
        
        projects = self.db_manager.get_all_projects()
        for project in projects:
            self.projects_tree.insert("", tk.END, iid=project.project_id, values=(
                project.name,
                project.description or "",
                format_date(project.start_date),
                format_date(project.end_date),
                project.status,
                f"{project.progress}%"
            ))
    
    def refresh_tasks(self):
        """Refresh tasks list and switch to Tasks tab."""
        # Switch to Tasks tab (index 2: Dashboard=0, Projects=1, Tasks=2, ...)
        if hasattr(self, 'notebook') and self.notebook is not None:
            self.notebook.select(2)
        
        # Check if tasks_tree exists
        if not hasattr(self, 'tasks_tree') or self.tasks_tree is None:
            return
        
        for item in self.tasks_tree.get_children():
            self.tasks_tree.delete(item)
        
        tasks = self.db_manager.get_all_tasks()
        projects = {p.project_id: p.name for p in self.db_manager.get_all_projects()}
        users = {u.user_id: u.username for u in self.db_manager.get_all_users()}
        
        for task in tasks:
            project_name = projects.get(task.project_id, "Unknown")
            assignee_name = users.get(task.assignee_id, "Unassigned") if task.assignee_id else "Unassigned"
            
            # Use task_id as item ID for easy retrieval
            self.tasks_tree.insert("", tk.END, iid=task.task_id, values=(
                project_name,
                task.name,
                assignee_name,
                task.status,
                task.priority,
                format_date(task.due_date),
                f"{task.progress}%"
            ))
    
    def refresh_licenses(self):
        """Refresh licenses list."""
        # Check if licenses_tree exists
        if not hasattr(self, 'licenses_tree') or self.licenses_tree is None:
            return
        
        for item in self.licenses_tree.get_children():
            self.licenses_tree.delete(item)
        
        # For normal users, only show their own license; admins see all licenses
        if self.auth_manager.is_admin():
            licenses = self.license_manager.get_all_licenses()
            users = {u.user_id: u.username for u in self.db_manager.get_all_users()}
        else:
            # Normal user - only show their own license
            current_user = self.auth_manager.get_current_user()
            if current_user:
                licenses = self.license_manager.get_license_by_user(current_user.user_id)
                users = {current_user.user_id: current_user.username}
            else:
                licenses = []
                users = {}
        
        for license in licenses:
            user_name = users.get(license.user_id, "Unknown") if license.user_id else "Unassigned"
            if self.auth_manager.is_admin():
                # Admin sees all licenses with user column
                self.licenses_tree.insert("", tk.END, values=(
                    license.license_key,
                    user_name,
                    format_date(license.issue_date),
                    format_date(license.expiry_date),
                    license.status
                ))
            else:
                # Normal user sees only their license without user column
                self.licenses_tree.insert("", tk.END, values=(
                    license.license_key,
                    format_date(license.issue_date),
                    format_date(license.expiry_date),
                    license.status
                ))
    
    def refresh_allocation(self):
        """Refresh task allocation data."""
        # Check if allocation_tree exists
        if not hasattr(self, 'allocation_tree') or self.allocation_tree is None:
            return
        
        for item in self.allocation_tree.get_children():
            self.allocation_tree.delete(item)
        
        workload_data = self.task_allocation.get_all_users_workload()
        for user_id, data in workload_data.items():
            workload = data['workload']
            self.allocation_tree.insert("", tk.END, values=(
                data['user'].username,
                workload['total_tasks'],
                workload['pending'],
                workload['in_progress'],
                workload['completed'],
                f"{workload['score']}/100"
            ))
    
    def refresh_risks(self):
        """Refresh risks list."""
        # Check if risks_tree exists
        if not hasattr(self, 'risks_tree') or self.risks_tree is None:
            return
        
        for item in self.risks_tree.get_children():
            self.risks_tree.delete(item)
        
        risks = self.risk_warning.get_all_risks()
        projects = {p.project_id: p.name for p in self.db_manager.get_all_projects()}
        
        for risk in risks:
            project_name = projects.get(risk.project_id, "Unknown")
            self.risks_tree.insert("", tk.END, values=(
                project_name,
                risk.description,
                risk.severity,
                risk.status,
                risk.mitigation or "None"
            ))
    
    def update_project_combo(self):
        """Update project combo box."""
        # Check if viz_project_combo exists
        if not hasattr(self, 'viz_project_combo') or self.viz_project_combo is None:
            return
        
        projects = self.db_manager.get_all_projects()
        project_names = ["All Projects"] + [f"{p.name} (ID: {p.project_id})" for p in projects]
        self.viz_project_combo['values'] = project_names
        if project_names:
            self.viz_project_combo.current(0)
    
    def update_visualization(self, event=None):
        """Update visualization charts."""
        # Check if required components exist
        if not hasattr(self, 'progress_chart_frame') or self.progress_chart_frame is None:
            return
        if not hasattr(self, 'task_chart_frame') or self.task_chart_frame is None:
            return
        if not hasattr(self, 'viz_project_var') or self.viz_project_var is None:
            return
        
        # Clear existing charts
        for widget in self.progress_chart_frame.winfo_children():
            widget.destroy()
        for widget in self.task_chart_frame.winfo_children():
            widget.destroy()
        
        # Get selected project
        selected = self.viz_project_var.get()
        project_id = None
        if selected and selected != "All Projects":
            try:
                project_id = int(selected.split("ID: ")[1].split(")")[0])
            except:
                pass
        
        # Create progress bar chart
        canvas = self.progress_visualizer.create_progress_bar_chart(self.progress_chart_frame, project_id)
        if canvas:
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Create task status pie chart
        canvas2 = self.progress_visualizer.create_task_status_pie_chart(self.task_chart_frame, project_id)
        if canvas2:
            canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Dialog methods
    def show_new_project_dialog(self):
        """Show new project dialog."""
        dialog = tk.Toplevel(self.window)
        dialog.title("New Project")
        dialog.geometry("400x350")
        dialog.transient(self.window)
        dialog.grab_set()
        
        tk.Label(dialog, text=self.lang.t('project_name_label')).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text=self.lang.t('description_label')).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        desc_text = tk.Text(dialog, width=30, height=5)
        desc_text.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text=self.lang.t('start_date_label')).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        start_entry = tk.Entry(dialog, width=30)
        start_entry.grid(row=2, column=1, padx=10, pady=10)
        start_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        tk.Label(dialog, text=self.lang.t('end_date_label')).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        end_entry = tk.Entry(dialog, width=30)
        end_entry.grid(row=3, column=1, padx=10, pady=10)
        
        def create_project():
            name = name_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            start_date = start_entry.get().strip()
            end_date = end_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Project name is required.")
                return
            
            # Validate start date format
            if not start_date:
                messagebox.showerror("Error", "Start date is required.")
                return
            
            if not validate_date(start_date):
                messagebox.showerror("Error", "Start date must be in YYYY-MM-DD format (e.g., 2024-01-15).")
                return
            
            # Validate start date is reasonable
            is_valid, error_msg = validate_date_reasonable(start_date)
            if not is_valid:
                messagebox.showerror("Error", error_msg)
                return
            
            # Validate end date format
            if not end_date:
                messagebox.showerror("Error", "End date is required.")
                return
            
            if not validate_date(end_date):
                messagebox.showerror("Error", "End date must be in YYYY-MM-DD format (e.g., 2024-12-31).")
                return
            
            # Validate end date is reasonable
            is_valid, error_msg = validate_date_reasonable(end_date)
            if not is_valid:
                messagebox.showerror("Error", error_msg)
                return
            
            # Validate date range (end after start)
            is_valid, error_msg = validate_date_range(start_date, end_date)
            if not is_valid:
                messagebox.showerror("Error", error_msg)
                return
            
            try:
                self.db_manager.create_project(name, description, start_date, end_date)
                messagebox.showinfo(self.lang.t('success'), self.lang.t('success_created', item=self.lang.t('projects')))
                self.refresh_projects()
                self.refresh_dashboard()
                self.update_project_combo()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror(self.lang.t('error'), self.lang.t('error_operation_failed', operation=self.lang.t('create').lower()))
        
        tk.Button(dialog, text="Create", command=create_project, bg="#4CAF50", fg="white").grid(row=4, column=1, padx=10, pady=20, sticky=tk.E)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=4, column=0, padx=10, pady=20, sticky=tk.W)
    
    def delete_selected_project(self):
        """Delete the selected project."""
        # Check if projects_tree exists
        if not hasattr(self, 'projects_tree') or self.projects_tree is None:
            messagebox.showwarning("Warning", "Please select a project to delete.")
            return
        
        selection = self.projects_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a project to delete.")
            return
        
        project_id = int(selection[0])
        
        # Get project info for confirmation
        projects = self.db_manager.get_all_projects()
        project = None
        for p in projects:
            if p.project_id == project_id:
                project = p
                break
        
        if not project:
            messagebox.showerror("Error", "Project not found.")
            return
        
        # Get related tasks and risks count
        tasks = self.db_manager.get_tasks_by_project(project_id)
        risks = self.db_manager.get_risks_by_project(project_id)
        
        # Confirmation dialog
        warning_msg = f"Are you sure you want to delete project '{project.name}'?\n\n"
        warning_msg += f"This will also delete:\n"
        warning_msg += f"  - {len(tasks)} task(s)\n"
        warning_msg += f"  - {len(risks)} risk(s)\n\n"
        warning_msg += "This action cannot be undone!"
        
        if not messagebox.askyesno("Confirm Delete", warning_msg):
            return
        
        # Delete project
        if self.db_manager.delete_project(project_id):
            messagebox.showinfo("Success", f"Project '{project.name}' and all related data have been deleted.")
            self.refresh_projects()
            self.refresh_dashboard()
            self.refresh_tasks()
            self.refresh_risks()
            self.update_project_combo()
        else:
            messagebox.showerror("Error", "Failed to delete project.")
    
    def show_new_task_dialog(self):
        """Show new task dialog."""
        dialog = tk.Toplevel(self.window)
        dialog.title("New Task")
        dialog.geometry("450x400")
        dialog.transient(self.window)
        dialog.grab_set()
        
        projects = self.db_manager.get_all_projects()
        users = self.db_manager.get_all_users()
        
        tk.Label(dialog, text="Project:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        project_var = tk.StringVar()
        project_combo = ttk.Combobox(dialog, textvariable=project_var, state="readonly", width=27)
        project_combo['values'] = [f"{p.name} (ID: {p.project_id})" for p in projects]
        project_combo.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Task Name:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        desc_text = tk.Text(dialog, width=30, height=4)
        desc_text.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Assignee:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        assignee_var = tk.StringVar()
        assignee_combo = ttk.Combobox(dialog, textvariable=assignee_var, state="readonly", width=27)
        assignee_combo['values'] = ["Unassigned"] + [f"{u.username} (ID: {u.user_id})" for u in users]
        assignee_combo.current(0)
        assignee_combo.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Priority:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        priority_var = tk.StringVar(value="medium")
        priority_combo = ttk.Combobox(dialog, textvariable=priority_var, state="readonly", width=27)
        priority_combo['values'] = ["low", "medium", "high", "critical"]
        priority_combo.grid(row=4, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Due Date (YYYY-MM-DD):").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        due_entry = tk.Entry(dialog, width=30)
        due_entry.grid(row=5, column=1, padx=10, pady=10)
        
        def create_task():
            project_selected = project_var.get()
            name = name_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            assignee_selected = assignee_var.get()
            priority = priority_var.get()
            due_date = due_entry.get().strip() or None
            
            if not name or not project_selected:
                messagebox.showerror("Error", "Task name and project are required.")
                return
            
            # Validate due date if provided (due date is optional)
            if due_date:
                if not validate_date(due_date):
                    messagebox.showerror("Error", "Due date must be in YYYY-MM-DD format (e.g., 2024-12-31).")
                    return
                
                # Validate due date is reasonable
                is_valid, error_msg = validate_date_reasonable(due_date)
                if not is_valid:
                    messagebox.showerror("Error", error_msg)
                    return
            
            try:
                project_id = int(project_selected.split("ID: ")[1].split(")")[0])
                
                # Check if task with same name and due date already exists in this project
                if self.db_manager.task_exists_in_project(project_id, name, due_date):
                    project_name = project_selected.split(" (ID:")[0]
                    if due_date:
                        messagebox.showerror("Error", f"A task with the name '{name}' and due date '{due_date}' already exists in project '{project_name}'.\n\nPlease use a different task name or due date.")
                    else:
                        messagebox.showerror("Error", f"A task with the name '{name}' and no due date already exists in project '{project_name}'.\n\nPlease use a different task name or set a due date.")
                    return
                
                assignee_id = None
                if assignee_selected != "Unassigned":
                    assignee_id = int(assignee_selected.split("ID: ")[1].split(")")[0])
                
                self.db_manager.create_task(project_id, name, description, assignee_id, 'pending', priority, due_date)
                messagebox.showinfo("Success", "Task created successfully.")
                self.refresh_tasks()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create task: {str(e)}")
        
        tk.Button(dialog, text="Create", command=create_task, bg="#4CAF50", fg="white").grid(row=6, column=1, padx=10, pady=20, sticky=tk.E)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=6, column=0, padx=10, pady=20, sticky=tk.W)
    
    def show_edit_task_dialog(self):
        """Show edit task dialog."""
        # Check if a task is selected
        selection = self.tasks_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to edit.")
            return
        
        # Get task ID from selection
        task_id = int(selection[0])
        
        # Get task details
        task = self.db_manager.get_task_by_id(task_id)
        if not task:
            messagebox.showerror("Error", "Task not found.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Edit Task")
        dialog.geometry("450x450")
        dialog.transient(self.window)
        dialog.grab_set()
        
        projects = self.db_manager.get_all_projects()
        users = self.db_manager.get_all_users()
        
        # Get project name for display
        project_name = None
        for p in projects:
            if p.project_id == task.project_id:
                project_name = f"{p.name} (ID: {p.project_id})"
                break
        
        tk.Label(dialog, text="Project:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        project_var = tk.StringVar(value=project_name)
        project_combo = ttk.Combobox(dialog, textvariable=project_var, state="readonly", width=27)
        project_combo['values'] = [f"{p.name} (ID: {p.project_id})" for p in projects]
        project_combo.grid(row=0, column=1, padx=10, pady=10)
        project_combo.config(state="disabled")  # Don't allow changing project
        
        tk.Label(dialog, text="Task Name:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        name_entry = tk.Entry(dialog, width=30)
        name_entry.insert(0, task.name)
        name_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Description:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        desc_text = tk.Text(dialog, width=30, height=4)
        desc_text.insert("1.0", task.description or "")
        desc_text.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Assignee:").grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        assignee_var = tk.StringVar()
        assignee_combo = ttk.Combobox(dialog, textvariable=assignee_var, state="readonly", width=27)
        assignee_combo['values'] = ["Unassigned"] + [f"{u.username} (ID: {u.user_id})" for u in users]
        if task.assignee_id:
            for u in users:
                if u.user_id == task.assignee_id:
                    assignee_var.set(f"{u.username} (ID: {u.user_id})")
                    break
        else:
            assignee_var.set("Unassigned")
        assignee_combo.grid(row=3, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Status:").grid(row=4, column=0, padx=10, pady=10, sticky=tk.W)
        status_var = tk.StringVar(value=task.status)
        status_combo = ttk.Combobox(dialog, textvariable=status_var, state="readonly", width=27)
        status_combo['values'] = ["pending", "in_progress", "completed", "blocked"]
        status_combo.grid(row=4, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Priority:").grid(row=5, column=0, padx=10, pady=10, sticky=tk.W)
        priority_var = tk.StringVar(value=task.priority)
        priority_combo = ttk.Combobox(dialog, textvariable=priority_var, state="readonly", width=27)
        priority_combo['values'] = ["low", "medium", "high", "critical"]
        priority_combo.grid(row=5, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Due Date (YYYY-MM-DD):").grid(row=6, column=0, padx=10, pady=10, sticky=tk.W)
        due_entry = tk.Entry(dialog, width=30)
        if task.due_date:
            due_entry.insert(0, task.due_date)
        due_entry.grid(row=6, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Progress (%):").grid(row=7, column=0, padx=10, pady=10, sticky=tk.W)
        progress_var = tk.StringVar(value=str(task.progress))
        progress_entry = tk.Entry(dialog, width=30, textvariable=progress_var)
        progress_entry.grid(row=7, column=1, padx=10, pady=10)
        
        def update_task():
            name = name_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            assignee_selected = assignee_var.get()
            status = status_var.get()
            priority = priority_var.get()
            due_date = due_entry.get().strip() or None
            progress_str = progress_var.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Task name is required.")
                return
            
            # Validate due date if provided
            if due_date:
                if not validate_date(due_date):
                    messagebox.showerror("Error", "Due date must be in YYYY-MM-DD format (e.g., 2024-12-31).")
                    return
                
                is_valid, error_msg = validate_date_reasonable(due_date)
                if not is_valid:
                    messagebox.showerror("Error", error_msg)
                    return
            
            # Validate progress
            try:
                progress = int(progress_str)
                if progress < 0 or progress > 100:
                    messagebox.showerror("Error", "Progress must be between 0 and 100.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Progress must be a number between 0 and 100.")
                return
            
            try:
                project_id = task.project_id  # Keep original project
                
                # Check if task with same name and due date already exists in this project (excluding current task)
                if self.db_manager.task_exists_in_project(project_id, name, due_date, exclude_task_id=task_id):
                    project_name = project_var.get().split(" (ID:")[0]
                    if due_date:
                        messagebox.showerror("Error", f"A task with the name '{name}' and due date '{due_date}' already exists in project '{project_name}'.\n\nPlease use a different task name or due date.")
                    else:
                        messagebox.showerror("Error", f"A task with the name '{name}' and no due date already exists in project '{project_name}'.\n\nPlease use a different task name or set a due date.")
                    return
                
                assignee_id = None
                if assignee_selected != "Unassigned":
                    assignee_id = int(assignee_selected.split("ID: ")[1].split(")")[0])
                
                self.db_manager.update_task(task_id, name, description, assignee_id, status, priority, due_date, progress)
                messagebox.showinfo("Success", "Task updated successfully.")
                self.refresh_tasks()
                self.refresh_projects()
                self.refresh_dashboard()
                self.update_project_combo()
                self.update_visualization()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update task: {str(e)}")
        
        tk.Button(dialog, text="Update", command=update_task, bg="#FF9800", fg="white").grid(row=8, column=1, padx=10, pady=20, sticky=tk.E)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=8, column=0, padx=10, pady=20, sticky=tk.W)
    
    def mark_task_complete(self):
        """Mark the selected task as completed."""
        # Check if tasks_tree exists
        if not hasattr(self, 'tasks_tree') or self.tasks_tree is None:
            messagebox.showwarning("Warning", "Please select a task to mark as complete.")
            return
        
        selection = self.tasks_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to mark as complete.")
            return
        
        # Get task ID from selection (item ID is task_id)
        task_id = int(selection[0])
        
        # Get task info
        item = self.tasks_tree.item(selection[0])
        task_name = item['values'][1] if len(item['values']) > 1 else "Unknown"
        current_status = item['values'][3] if len(item['values']) > 3 else "Unknown"
        
        # Check if already completed
        if current_status == 'completed':
            messagebox.showinfo("Info", f"Task '{task_name}' is already marked as completed.")
            return
        
        # Update task status to completed and progress to 100%
        try:
            self.db_manager.update_task_status(task_id, 'completed', 100)
            
            # Update project progress based on completed tasks
            tasks = self.db_manager.get_all_tasks()
            project_tasks = {}
            for task in tasks:
                if task.project_id not in project_tasks:
                    project_tasks[task.project_id] = {'total': 0, 'completed': 0}
                project_tasks[task.project_id]['total'] += 1
                if task.status == 'completed':
                    project_tasks[task.project_id]['completed'] += 1
            
            # Update project progress
            for project_id, counts in project_tasks.items():
                if counts['total'] > 0:
                    progress = int((counts['completed'] / counts['total']) * 100)
                    self.db_manager.update_project_progress(project_id, progress)
            
            messagebox.showinfo("Success", f"Task '{task_name}' has been marked as completed.")
            self.refresh_tasks()
            self.refresh_projects()
            self.refresh_dashboard()
            self.refresh_allocation()
            self.update_project_combo()
            self.update_visualization()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark task as complete: {str(e)}")
    
    def delete_selected_task(self):
        """Delete the selected task."""
        # Check if tasks_tree exists
        if not hasattr(self, 'tasks_tree') or self.tasks_tree is None:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        
        selection = self.tasks_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        
        # Get task ID from selection (item ID is task_id)
        task_id = int(selection[0])
        
        # Get task info for confirmation
        item = self.tasks_tree.item(selection[0])
        task_name = item['values'][1] if len(item['values']) > 1 else "Unknown"
        
        # Confirmation dialog
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task '{task_name}'?\n\nThis action cannot be undone!"):
            return
        
        # Delete task
        if self.db_manager.delete_task(task_id):
            # Update project progress after task deletion
            tasks = self.db_manager.get_all_tasks()
            project_tasks = {}
            for task in tasks:
                if task.project_id not in project_tasks:
                    project_tasks[task.project_id] = {'total': 0, 'completed': 0}
                project_tasks[task.project_id]['total'] += 1
                if task.status == 'completed':
                    project_tasks[task.project_id]['completed'] += 1
            
            # Update project progress
            for project_id, counts in project_tasks.items():
                if counts['total'] > 0:
                    progress = int((counts['completed'] / counts['total']) * 100)
                    self.db_manager.update_project_progress(project_id, progress)
            
            messagebox.showinfo("Success", f"Task '{task_name}' has been deleted.")
            self.refresh_tasks()
            self.refresh_projects()
            self.refresh_dashboard()
            self.refresh_allocation()
            self.update_project_combo()
        else:
            messagebox.showerror("Error", "Failed to delete task.")
    
    def show_generate_license_dialog(self):
        """Show generate license dialog."""
        # Check if user is admin before allowing license generation
        if not self.auth_manager.is_admin():
            messagebox.showerror("Access Denied", "Only administrators can generate licenses.")
            return
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Generate License")
        dialog.geometry("400x180")
        dialog.transient(self.window)
        dialog.grab_set()
        
        tk.Label(dialog, text="Validity (days):").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        days_entry = tk.Entry(dialog, width=30)
        days_entry.insert(0, "365")
        days_entry.grid(row=0, column=1, padx=10, pady=10)
        
        def generate_license():
            try:
                days = int(days_entry.get())
                # Create unassigned license (user_id = None)
                license_id, license_key = self.license_manager.create_license(None, days)
                messagebox.showinfo("License Generated", f"License created successfully!\n\nLicense Key: {license_key}")
                self.refresh_licenses()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to generate license: {str(e)}")
        
        tk.Button(dialog, text="Generate", command=generate_license, bg="#4CAF50", fg="white").grid(row=1, column=1, padx=10, pady=20, sticky=tk.E)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=1, column=0, padx=10, pady=20, sticky=tk.W)
    
    def show_add_risk_dialog(self):
        """Show add risk dialog."""
        dialog = tk.Toplevel(self.window)
        dialog.title("Add Risk")
        dialog.geometry("450x300")
        dialog.transient(self.window)
        dialog.grab_set()
        
        projects = self.db_manager.get_all_projects()
        
        tk.Label(dialog, text="Project:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        project_var = tk.StringVar()
        project_combo = ttk.Combobox(dialog, textvariable=project_var, state="readonly", width=27)
        project_combo['values'] = [f"{p.name} (ID: {p.project_id})" for p in projects]
        project_combo.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        desc_text = tk.Text(dialog, width=30, height=6)
        desc_text.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Severity:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        severity_var = tk.StringVar(value="medium")
        severity_combo = ttk.Combobox(dialog, textvariable=severity_var, state="readonly", width=27)
        severity_combo['values'] = ["low", "medium", "high", "critical"]
        severity_combo.grid(row=2, column=1, padx=10, pady=10)
        
        def add_risk():
            project_selected = project_var.get()
            description = desc_text.get("1.0", tk.END).strip()
            severity = severity_var.get()
            
            if not description or not project_selected:
                messagebox.showerror("Error", "Description and project are required.")
                return
            
            try:
                project_id = int(project_selected.split("ID: ")[1].split(")")[0])
                self.risk_warning.create_risk_alert(project_id, description, severity)
                messagebox.showinfo("Success", "Risk added successfully.")
                self.refresh_risks()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add risk: {str(e)}")
        
        tk.Button(dialog, text="Add", command=add_risk, bg="#F44336", fg="white").grid(row=3, column=1, padx=10, pady=20, sticky=tk.E)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).grid(row=3, column=0, padx=10, pady=20, sticky=tk.W)
    
    def show_workload_report(self):
        """Show workload balance report."""
        report = self.task_allocation.get_workload_balance_report()
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Workload Balance Report")
        dialog.geometry("600x500")
        dialog.transient(self.window)
        
        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        report_text = "WORKLOAD BALANCE REPORT\n"
        report_text += "=" * 50 + "\n\n"
        report_text += f"Average Workload: {report['average_workload']:.1f}/100\n"
        report_text += f"Max Workload: {report['max_workload']}/100\n"
        report_text += f"Min Workload: {report['min_workload']}/100\n\n"
        report_text += "User Details:\n"
        report_text += "-" * 50 + "\n"
        
        for user in report['users']:
            report_text += f"\n{user['username']}:\n"
            report_text += f"  - Workload Score: {user['workload_score']}/100\n"
            report_text += f"  - Active Tasks: {user['active_tasks']}\n"
            report_text += f"  - Total Tasks: {user['total_tasks']}\n"
        
        if report['recommendations']:
            report_text += "\n\nRecommendations:\n"
            report_text += "-" * 50 + "\n"
            for rec in report['recommendations']:
                report_text += f"• {rec}\n"
        
        text_widget.insert("1.0", report_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_risk_summary(self):
        """Show risk summary."""
        summary = self.risk_warning.get_risk_summary()
        
        dialog = tk.Toplevel(self.window)
        dialog.title("Risk Summary")
        dialog.geometry("700x600")
        dialog.transient(self.window)
        
        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        summary_text = "RISK SUMMARY\n"
        summary_text += "=" * 50 + "\n\n"
        summary_text += f"Total Projects: {summary['total_projects']}\n"
        summary_text += f"Total Risks: {summary['total_risks']}\n"
        summary_text += f"Open Risks: {summary['open_risks']}\n\n"
        summary_text += "Risks by Severity:\n"
        summary_text += f"  - Critical: {summary['by_severity']['critical']}\n"
        summary_text += f"  - High: {summary['by_severity']['high']}\n"
        summary_text += f"  - Medium: {summary['by_severity']['medium']}\n"
        summary_text += f"  - Low: {summary['by_severity']['low']}\n\n"
        
        if summary['projects_with_risks']:
            summary_text += "Projects with Risks:\n"
            summary_text += "-" * 50 + "\n"
            for project_analysis in summary['projects_with_risks']:
                summary_text += f"\n{project_analysis['project_name']}:\n"
                summary_text += f"  - Open Risks: {project_analysis['open_risks']}\n"
                summary_text += f"  - Critical: {project_analysis['critical_risks']}\n"
                summary_text += f"  - High: {project_analysis['high_risks']}\n"
                if project_analysis['warnings']:
                    summary_text += "  - Warnings:\n"
                    for warning in project_analysis['warnings']:
                        summary_text += f"    • {warning}\n"
        
        text_widget.insert("1.0", summary_text)
        text_widget.config(state=tk.DISABLED)
    
    def on_project_select(self, event):
        """Handle project selection."""
        # Check if projects_tree exists
        if not hasattr(self, 'projects_tree') or self.projects_tree is None:
            return
        
        selection = self.projects_tree.selection()
        if selection:
            project_id = int(selection[0])
            # Switch to visualization tab and show project
            # Progress Visualization is the 5th tab (index 4: Dashboard=0, Projects=1, Tasks=2, License=3, Visualization=4)
            self.notebook.select(4)
            # Set project in combo
            if hasattr(self, 'viz_project_combo') and self.viz_project_combo is not None:
                projects = self.db_manager.get_all_projects()
                for i, p in enumerate(projects):
                    if p.project_id == project_id:
                        self.viz_project_combo.current(i + 1)
                        self.update_visualization()
                        break
    
    def check_risk_alerts(self):
        """Check and display risk alerts."""
        alerts = self.risk_warning.get_immediate_alerts()
        if alerts:
            alert_text = "RISK ALERTS\n\n"
            for alert in alerts:
                alert_text += f"⚠ {alert['message']}\n"
            messagebox.showwarning("Risk Alerts", alert_text)
    
    def show_license_management(self):
        """Switch to license management tab."""
        if hasattr(self, 'notebook') and self.notebook is not None:
            # License Management is the 4th tab (index 3)
            self.notebook.select(3)
    
    def show_progress_visualization(self):
        """Switch to progress visualization tab."""
        if hasattr(self, 'notebook') and self.notebook is not None:
            # Progress Visualization is the 5th tab (index 4)
            self.notebook.select(4)
    
    def show_task_allocation(self):
        """Switch to task allocation tab."""
        if hasattr(self, 'notebook') and self.notebook is not None:
            # Task Allocation is the 6th tab (index 5)
            self.notebook.select(5)
    
    def show_risk_warning(self):
        """Switch to risk warning tab."""
        if hasattr(self, 'notebook') and self.notebook is not None:
            # Risk Warning is the 7th tab (index 6)
            self.notebook.select(6)
    
    def logout(self):
        """Handle logout."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.auth_manager.logout()
            self.window.destroy()
            # Restart login window with callback
            from ui.login_window import LoginWindow
            def on_success(auth_manager):
                from ui.main_window import MainWindow
                main_window = MainWindow(auth_manager)
                main_window.run()
            login = LoginWindow(on_success)
            login.run()
    
    def run(self):
        """Run the main window."""
        self.window.mainloop()

