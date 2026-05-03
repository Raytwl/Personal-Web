"""
Helper utility functions for TeamAxis.
"""

from datetime import datetime

def format_date(date_string):
    """Format date string for display."""
    if not date_string:
        return "N/A"
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%Y-%m-%d')
    except:
        return date_string

def validate_date(date_string):
    """Validate date string format."""
    if not date_string or not date_string.strip():
        return False
    try:
        datetime.strptime(date_string.strip(), '%Y-%m-%d')
        return True
    except:
        return False

def validate_date_range(start_date, end_date):
    """Validate that end date is after start date."""
    if not start_date or not end_date:
        return True, None  # If either is empty, skip range validation
    
    if not validate_date(start_date) or not validate_date(end_date):
        return False, "Invalid date format"
    
    try:
        start = datetime.strptime(start_date.strip(), '%Y-%m-%d').date()
        end = datetime.strptime(end_date.strip(), '%Y-%m-%d').date()
        
        if end < start:
            return False, "End date must be after start date"
        
        return True, None
    except Exception as e:
        return False, f"Date validation error: {str(e)}"

def validate_date_reasonable(date_string):
    """Validate that date is within reasonable range (1900-2100)."""
    if not date_string or not date_string.strip():
        return True, None
    
    if not validate_date(date_string):
        return False, "Invalid date format"
    
    try:
        date_obj = datetime.strptime(date_string.strip(), '%Y-%m-%d').date()
        year = date_obj.year
        
        if year < 1900 or year > 2100:
            return False, "Date year must be between 1900 and 2100"
        
        return True, None
    except Exception as e:
        return False, f"Date validation error: {str(e)}"

def calculate_progress(completed, total):
    """Calculate progress percentage."""
    if total == 0:
        return 0
    return int((completed / total) * 100)

def get_status_color(status):
    """Get color code for status."""
    colors = {
        'active': '#4CAF50',
        'completed': '#2196F3',
        'on_hold': '#FF9800',
        'cancelled': '#F44336',
        'pending': '#FFC107',
        'in_progress': '#2196F3',
        'blocked': '#F44336'
    }
    return colors.get(status, '#757575')

def get_priority_color(priority):
    """Get color code for priority."""
    colors = {
        'low': '#4CAF50',
        'medium': '#FF9800',
        'high': '#FF5722',
        'critical': '#F44336'
    }
    return colors.get(priority, '#757575')

def get_severity_color(severity):
    """Get color code for risk severity."""
    colors = {
        'low': '#4CAF50',
        'medium': '#FF9800',
        'high': '#FF5722',
        'critical': '#F44336'
    }
    return colors.get(severity, '#757575')

