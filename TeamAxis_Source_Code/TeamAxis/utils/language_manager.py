"""
Language manager for TeamAxis multi-language support.
Supports English and Traditional Chinese.
"""

import json
import os

class LanguageManager:
    """Manages language translations and switching."""
    
    # Translation dictionaries
    TRANSLATIONS = {
        'en': {
            # Application
            'app_title': 'TeamAxis - Project Management System',
            'app_title_login': 'TeamAxis - Login',
            'app_name': 'TeamAxis',
            'app_subtitle': 'Project Management System',
            
            # Login Window
            'username': 'Username:',
            'password': 'Password:',
            'license_key': 'License Key:',
            'license_format_hint': 'Format: XXXX-XXXX-XXXX-XXXX',
            'login': 'Login',
            'register': 'Register',
            'default_credentials': '',
            
            # Registration
            'create_new_account': 'Create New Account',
            'confirm_password': 'Confirm Password:',
            'email': 'Email:',
            'license_required': 'Format: XXXX-XXXX-XXXX-XXXX (Required)',
            
            # Menu
            'menu_file': 'File',
            'menu_projects': 'Projects',
            'menu_tasks': 'Tasks',
            'menu_license': 'License',
            'menu_features': 'Features',
            'menu_language': 'Language',
            'menu_logout': 'Logout',
            'menu_exit': 'Exit',
            'menu_new_project': 'New Project',
            'menu_view_all_projects': 'View All Projects',
            'menu_new_task': 'New Task',
            'menu_view_all_tasks': 'View All Tasks',
            'menu_manage_licenses': 'Manage Licenses',
            'menu_progress_visualization': 'Progress Visualization',
            'menu_task_allocation': 'Task Allocation',
            'menu_risk_warning': 'Risk Warning',
            'menu_english': 'English',
            'menu_traditional_chinese': '繁體中文',
            'menu_theme': 'Theme',
            'menu_light_theme': 'Light',
            'menu_dark_theme': 'Dark',
            
            # Dashboard
            'dashboard': 'Dashboard',
            'welcome': 'Welcome, {username}!',
            'total_projects': 'Total Projects',
            'total_tasks': 'Total Tasks',
            'open_risks': 'Open Risks',
            'active_projects': 'Active Projects',
            'recent_projects': 'Recent Projects',
            'project_name': 'Project Name',
            'status': 'Status',
            'progress': 'Progress %',
            
            # Projects
            'projects': 'Projects',
            'new_project': 'New Project',
            'edit_project': 'Edit Project',
            'delete_project': 'Delete Project',
            'refresh': 'Refresh',
            'description': 'Description',
            'start_date': 'Start Date',
            'end_date': 'End Date',
            'project_name_label': 'Project Name:',
            'start_date_label': 'Start Date (YYYY-MM-DD):',
            'end_date_label': 'End Date (YYYY-MM-DD):',
            
            # Tasks
            'tasks': 'Tasks',
            'new_task': 'New Task',
            'edit_task': 'Edit Task',
            'mark_as_complete': 'Mark as Complete',
            'delete_task': 'Delete Task',
            'task_name': 'Task Name',
            'assignee': 'Assignee',
            'priority': 'Priority',
            'due_date': 'Due Date',
            'project': 'Project',
            'task_name_label': 'Task Name:',
            'assignee_label': 'Assignee:',
            'priority_label': 'Priority:',
            'due_date_label': 'Due Date (YYYY-MM-DD):',
            'progress_label': 'Progress (%):',
            'unassigned': 'Unassigned',
            
            # License Management
            'license_management': 'License Management',
            'generate_license': 'Generate License',
            'license_key_col': 'License Key',
            'user': 'User',
            'issue_date': 'Issue Date',
            'expiry_date': 'Expiry Date',
            'user_label': 'User:',
            'validity_days': 'Validity (days):',
            
            # Progress Visualization
            'progress_visualization': 'Progress Visualization',
            'select_project': 'Select Project:',
            'all_projects': 'All Projects',
            'refresh_charts': 'Refresh Charts',
            'project_progress_overview': 'Project Progress Overview',
            'task_status_distribution': 'Task Status Distribution',
            
            # Task Allocation
            'task_allocation': 'Task Allocation',
            'workload_report': 'Workload Report',
            'total_tasks_col': 'Total Tasks',
            'pending': 'Pending',
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'workload_score': 'Workload Score',
            
            # Risk Warning
            'risk_warning': 'Risk Warning',
            'add_risk': 'Add Risk',
            'risk_summary': 'Risk Summary',
            'severity': 'Severity',
            'mitigation': 'Mitigation',
            'project_label': 'Project:',
            'description_label': 'Description:',
            'severity_label': 'Severity:',
            
            # Status values
            'status_active': 'active',
            'status_completed': 'completed',
            'status_on_hold': 'on_hold',
            'status_cancelled': 'cancelled',
            'status_pending': 'pending',
            'status_blocked': 'blocked',
            
            # Priority values
            'priority_low': 'low',
            'priority_medium': 'medium',
            'priority_high': 'high',
            'priority_critical': 'critical',
            
            # Severity values
            'severity_low': 'low',
            'severity_medium': 'medium',
            'severity_high': 'high',
            'severity_critical': 'critical',
            
            # Buttons
            'create': 'Create',
            'update': 'Update',
            'cancel': 'Cancel',
            'save': 'Save',
            'delete': 'Delete',
            'generate': 'Generate',
            'add': 'Add',
            
            # Messages
            'success': 'Success',
            'error': 'Error',
            'warning': 'Warning',
            'info': 'Info',
            'confirm': 'Confirm',
            'yes': 'Yes',
            'no': 'No',
            
            # Error messages
            'error_required': 'is required.',
            'error_invalid_format': 'must be in YYYY-MM-DD format (e.g., 2024-01-15).',
            'error_date_range': 'Date year must be between 1900 and 2100',
            'error_end_before_start': 'End date must be after start date',
            'error_duplicate_task': "專案 '{project}' 中已存在名稱為 '{name}' 且到期日為 '{due_date}' 的任務。\n\n請使用不同的任務名稱或到期日。",
            'error_duplicate_task_no_date': "專案 '{project}' 中已存在名稱為 '{name}' 且無到期日的任務。\n\n請使用不同的任務名稱或設定到期日。",
            'error_select_item': 'Please select a {item} to {action}.',
            'error_not_found': '{item} not found.',
            'error_operation_failed': 'Failed to {operation}.',
            'success_created': '{item} created successfully.',
            'success_updated': '{item} updated successfully.',
            'success_deleted': '{item} deleted successfully.',
            'confirm_delete': "Are you sure you want to delete {item} '{name}'?\n\nThis action cannot be undone!",
            'confirm_logout': 'Are you sure you want to logout?',
        },
        'zh_TW': {
            # Application
            'app_title': 'TeamAxis - 專案管理系統',
            'app_title_login': 'TeamAxis - 登入',
            'app_name': 'TeamAxis',
            'app_subtitle': '專案管理系統',
            
            # Login Window
            'username': '使用者名稱:',
            'password': '密碼:',
            'license_key': '授權金鑰:',
            'license_format_hint': '格式: XXXX-XXXX-XXXX-XXXX',
            'login': '登入',
            'register': '註冊',
            'default_credentials': '',
            
            # Registration
            'create_new_account': '建立新帳號',
            'confirm_password': '確認密碼:',
            'email': '電子郵件:',
            'license_required': '格式: XXXX-XXXX-XXXX-XXXX (必填)',
            
            # Menu
            'menu_file': '檔案',
            'menu_projects': '專案',
            'menu_tasks': '任務',
            'menu_license': '授權',
            'menu_features': '功能',
            'menu_language': '語言',
            'menu_logout': '登出',
            'menu_exit': '結束',
            'menu_new_project': '新增專案',
            'menu_view_all_projects': '查看所有專案',
            'menu_new_task': '新增任務',
            'menu_view_all_tasks': '查看所有任務',
            'menu_manage_licenses': '管理授權',
            'menu_progress_visualization': '進度可視化',
            'menu_task_allocation': '任務分配',
            'menu_risk_warning': '風險警告',
            'menu_english': 'English',
            'menu_traditional_chinese': '繁體中文',
            'menu_theme': '主題',
            'menu_light_theme': '淺色',
            'menu_dark_theme': '深色',
            
            # Dashboard
            'dashboard': '儀表板',
            'welcome': '歡迎, {username}!',
            'total_projects': '總專案數',
            'total_tasks': '總任務數',
            'open_risks': '未解決風險',
            'active_projects': '進行中專案',
            'recent_projects': '最近專案',
            'project_name': '專案名稱',
            'status': '狀態',
            'progress': '進度 %',
            
            # Projects
            'projects': '專案',
            'new_project': '新增專案',
            'edit_project': '編輯專案',
            'delete_project': '刪除專案',
            'refresh': '重新整理',
            'description': '描述',
            'start_date': '開始日期',
            'end_date': '結束日期',
            'project_name_label': '專案名稱:',
            'start_date_label': '開始日期 (YYYY-MM-DD):',
            'end_date_label': '結束日期 (YYYY-MM-DD):',
            
            # Tasks
            'tasks': '任務',
            'new_task': '新增任務',
            'edit_task': '編輯任務',
            'mark_as_complete': '標記為完成',
            'delete_task': '刪除任務',
            'task_name': '任務名稱',
            'assignee': '負責人',
            'priority': '優先級',
            'due_date': '到期日',
            'project': '專案',
            'task_name_label': '任務名稱:',
            'assignee_label': '負責人:',
            'priority_label': '優先級:',
            'due_date_label': '到期日 (YYYY-MM-DD):',
            'progress_label': '進度 (%):',
            'unassigned': '未分配',
            
            # License Management
            'license_management': '授權管理',
            'generate_license': '產生授權',
            'license_key_col': '授權金鑰',
            'user': '使用者',
            'issue_date': '發行日期',
            'expiry_date': '到期日期',
            'user_label': '使用者:',
            'validity_days': '有效天數:',
            
            # Progress Visualization
            'progress_visualization': '進度視覺化',
            'select_project': '選擇專案:',
            'all_projects': '所有專案',
            'refresh_charts': '重新整理圖表',
            'project_progress_overview': '專案進度總覽',
            'task_status_distribution': '任務狀態分布',
            
            # Task Allocation
            'task_allocation': '任務分配',
            'workload_report': '工作負載報告',
            'total_tasks_col': '總任務數',
            'pending': '待處理',
            'in_progress': '進行中',
            'completed': '已完成',
            'workload_score': '工作負載分數',
            
            # Risk Warning
            'risk_warning': '風險警告',
            'add_risk': '新增風險',
            'risk_summary': '風險摘要',
            'severity': '嚴重程度',
            'mitigation': '緩解措施',
            'project_label': '專案:',
            'description_label': '描述:',
            'severity_label': '嚴重程度:',
            
            # Status values
            'status_active': '進行中',
            'status_completed': '已完成',
            'status_on_hold': '暫停',
            'status_cancelled': '已取消',
            'status_pending': '待處理',
            'status_blocked': '已阻擋',
            
            # Priority values
            'priority_low': '低',
            'priority_medium': '中',
            'priority_high': '高',
            'priority_critical': '緊急',
            
            # Severity values
            'severity_low': '低',
            'severity_medium': '中',
            'severity_high': '高',
            'severity_critical': '緊急',
            
            # Buttons
            'create': '建立',
            'update': '更新',
            'cancel': '取消',
            'save': '儲存',
            'delete': '刪除',
            'generate': '產生',
            'add': '新增',
            
            # Messages
            'success': '成功',
            'error': '錯誤',
            'warning': '警告',
            'info': '資訊',
            'confirm': '確認',
            'yes': '是',
            'no': '否',
            
            # Error messages
            'error_required': '為必填項目。',
            'error_invalid_format': '必須為 YYYY-MM-DD 格式 (例如: 2024-01-15)。',
            'error_date_range': '日期年份必須在 1900 到 2100 之間',
            'error_end_before_start': '結束日期必須在開始日期之後',
            'error_duplicate_task': "專案 '{project}' 中已存在名稱為 '{name}' 且到期日為 '{due_date}' 的任務。\n\n請使用不同的任務名稱或到期日。",
            'error_duplicate_task_no_date': "專案 '{project}' 中已存在名稱為 '{name}' 且無到期日的任務。\n\n請使用不同的任務名稱或設定到期日。",
            'error_select_item': '請選擇要{action}的{item}。',
            'error_not_found': '找不到{item}。',
            'error_operation_failed': '{operation}失敗。',
            'success_created': '{item}建立成功。',
            'success_updated': '{item}更新成功。',
            'success_deleted': '{item}刪除成功。',
            'confirm_delete': '您確定要刪除{item}「{name}」嗎？\n\n此操作無法復原！',
            'confirm_logout': '您確定要登出嗎？',
        }
    }
    
    def __init__(self, default_language='en'):
        """Initialize language manager."""
        self.current_language = default_language
        self.load_preference()
    
    def load_preference(self):
        """Load language preference from file."""
        config_file = 'language_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    lang = config.get('language', 'en')
                    if lang in self.TRANSLATIONS:
                        self.current_language = lang
            except:
                pass  # Use default if file is corrupted
    
    def save_preference(self):
        """Save language preference to file."""
        config_file = 'language_config.json'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({'language': self.current_language}, f, ensure_ascii=False, indent=2)
        except:
            pass  # Ignore save errors
    
    def set_language(self, language):
        """Set current language."""
        if language in self.TRANSLATIONS:
            self.current_language = language
            self.save_preference()
            return True
        return False
    
    def get(self, key, default=None, **kwargs):
        """Get translated string."""
        translation = self.TRANSLATIONS.get(self.current_language, {}).get(key, default)
        if translation and kwargs:
            try:
                return translation.format(**kwargs)
            except:
                return translation
        return translation if translation is not None else key
    
    def t(self, key, default=None, **kwargs):
        """Shortcut for get()."""
        return self.get(key, default, **kwargs)

# Global language manager instance
_language_manager = None

def get_language_manager():
    """Get global language manager instance."""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager

