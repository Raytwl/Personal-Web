"""
Tests for utils/helpers.py
"""

import pytest
from utils.helpers import (
    format_date, validate_date, validate_date_range,
    validate_date_reasonable, calculate_progress,
    get_status_color, get_priority_color, get_severity_color
)

class TestDateHelpers:
    """Test date-related helper functions."""
    
    def test_format_date_valid(self):
        """Test formatting valid date."""
        result = format_date('2024-01-15')
        assert result == '2024-01-15'
    
    def test_format_date_none(self):
        """Test formatting None date."""
        result = format_date(None)
        assert result == 'N/A'
    
    def test_format_date_empty(self):
        """Test formatting empty date."""
        result = format_date('')
        assert result == 'N/A'
    
    def test_format_date_invalid(self):
        """Test formatting invalid date."""
        result = format_date('invalid-date')
        assert result == 'invalid-date'  # Returns as-is if invalid
    
    def test_validate_date_valid(self):
        """Test validating valid date."""
        assert validate_date('2024-01-15') is True
        assert validate_date('2024-12-31') is True
        assert validate_date('2000-01-01') is True
    
    def test_validate_date_invalid_format(self):
        """Test validating invalid date format."""
        assert validate_date('01-15-2024') is False
        assert validate_date('2024/01/15') is False
        assert validate_date('15-01-2024') is False
    
    def test_validate_date_empty(self):
        """Test validating empty date."""
        assert validate_date('') is False
        assert validate_date(None) is False
        assert validate_date('   ') is False
    
    def test_validate_date_invalid_date(self):
        """Test validating invalid date values."""
        assert validate_date('2024-13-01') is False  # Invalid month
        assert validate_date('2024-02-30') is False  # Invalid day
        assert validate_date('2024-00-01') is False  # Invalid month
    
    def test_validate_date_range_valid(self):
        """Test validating valid date range."""
        valid, error = validate_date_range('2024-01-01', '2024-12-31')
        assert valid is True
        assert error is None
    
    def test_validate_date_range_invalid_order(self):
        """Test validating invalid date range (end before start)."""
        valid, error = validate_date_range('2024-12-31', '2024-01-01')
        assert valid is False
        assert 'after' in error.lower()
    
    def test_validate_date_range_same_date(self):
        """Test validating date range with same dates."""
        valid, error = validate_date_range('2024-01-01', '2024-01-01')
        assert valid is True  # Same date is considered valid
    
    def test_validate_date_range_empty(self):
        """Test validating date range with empty dates."""
        valid, error = validate_date_range('', '2024-12-31')
        assert valid is True  # Empty dates skip validation
        
        valid, error = validate_date_range('2024-01-01', '')
        assert valid is True
        
        valid, error = validate_date_range('', '')
        assert valid is True
    
    def test_validate_date_range_invalid_format(self):
        """Test validating date range with invalid format."""
        valid, error = validate_date_range('invalid', '2024-12-31')
        assert valid is False
        assert 'format' in error.lower()
    
    def test_validate_date_reasonable_valid(self):
        """Test validating reasonable date."""
        valid, error = validate_date_reasonable('2024-01-15')
        assert valid is True
        assert error is None
    
    def test_validate_date_reasonable_too_old(self):
        """Test validating date that's too old."""
        valid, error = validate_date_reasonable('1899-01-01')
        assert valid is False
        assert '1900' in error
    
    def test_validate_date_reasonable_too_future(self):
        """Test validating date that's too far in future."""
        valid, error = validate_date_reasonable('2101-01-01')
        assert valid is False
        assert '2100' in error
    
    def test_validate_date_reasonable_boundary(self):
        """Test validating date at boundaries."""
        valid, error = validate_date_reasonable('1900-01-01')
        assert valid is True
        
        valid, error = validate_date_reasonable('2100-12-31')
        assert valid is True
    
    def test_validate_date_reasonable_empty(self):
        """Test validating empty date (should pass)."""
        valid, error = validate_date_reasonable('')
        assert valid is True
        assert error is None

class TestProgressHelpers:
    """Test progress calculation functions."""
    
    def test_calculate_progress_normal(self):
        """Test normal progress calculation."""
        assert calculate_progress(50, 100) == 50
        assert calculate_progress(25, 100) == 25
        assert calculate_progress(75, 100) == 75
        assert calculate_progress(100, 100) == 100
    
    def test_calculate_progress_zero_total(self):
        """Test progress calculation with zero total."""
        assert calculate_progress(0, 0) == 0
        assert calculate_progress(10, 0) == 0
    
    def test_calculate_progress_fractional(self):
        """Test progress calculation with fractional results."""
        assert calculate_progress(1, 3) == 33  # 33.33... rounded to int
        assert calculate_progress(2, 3) == 66  # 66.66... rounded to int
    
    def test_calculate_progress_over_100(self):
        """Test progress calculation over 100%."""
        assert calculate_progress(150, 100) == 150

class TestColorHelpers:
    """Test color helper functions."""
    
    def test_get_status_color(self):
        """Test getting status colors."""
        assert get_status_color('active') == '#4CAF50'
        assert get_status_color('completed') == '#2196F3'
        assert get_status_color('on_hold') == '#FF9800'
        assert get_status_color('cancelled') == '#F44336'
        assert get_status_color('pending') == '#FFC107'
        assert get_status_color('in_progress') == '#2196F3'
        assert get_status_color('blocked') == '#F44336'
    
    def test_get_status_color_unknown(self):
        """Test getting color for unknown status."""
        assert get_status_color('unknown_status') == '#757575'
    
    def test_get_priority_color(self):
        """Test getting priority colors."""
        assert get_priority_color('low') == '#4CAF50'
        assert get_priority_color('medium') == '#FF9800'
        assert get_priority_color('high') == '#FF5722'
        assert get_priority_color('critical') == '#F44336'
    
    def test_get_priority_color_unknown(self):
        """Test getting color for unknown priority."""
        assert get_priority_color('unknown_priority') == '#757575'
    
    def test_get_severity_color(self):
        """Test getting severity colors."""
        assert get_severity_color('low') == '#4CAF50'
        assert get_severity_color('medium') == '#FF9800'
        assert get_severity_color('high') == '#FF5722'
        assert get_severity_color('critical') == '#F44336'
    
    def test_get_severity_color_unknown(self):
        """Test getting color for unknown severity."""
        assert get_severity_color('unknown_severity') == '#757575'

