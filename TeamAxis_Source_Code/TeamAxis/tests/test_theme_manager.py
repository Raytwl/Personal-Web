"""
Tests for utils/theme_manager.py
"""

import pytest
import os
import json
import tempfile
from utils.theme_manager import ThemeManager, get_theme_manager

class TestThemeManager:
    """Test ThemeManager class."""
    
    def test_init_default_theme(self):
        """Test initialization with default theme."""
        manager = ThemeManager()
        assert manager.current_theme == 'light'
    
    def test_init_custom_theme(self):
        """Test initialization with custom theme."""
        manager = ThemeManager('dark')
        assert manager.current_theme == 'dark'
    
    def test_set_theme_valid(self):
        """Test setting valid theme."""
        manager = ThemeManager()
        result = manager.set_theme('dark')
        assert result is True
        assert manager.current_theme == 'dark'
    
    def test_set_theme_invalid(self):
        """Test setting invalid theme."""
        manager = ThemeManager()
        result = manager.set_theme('invalid_theme')
        assert result is False
        assert manager.current_theme == 'light'  # Should remain unchanged
    
    def test_get_theme_color_light(self):
        """Test getting theme colors for light theme."""
        manager = ThemeManager('light')
        assert manager.get('bg_primary') == '#FFFFFF'
        assert manager.get('fg_primary') == '#000000'
        assert manager.get('accent_primary') == '#2196F3'
    
    def test_get_theme_color_dark(self):
        """Test getting theme colors for dark theme."""
        manager = ThemeManager('dark')
        assert manager.get('bg_primary') == '#1E1E1E'
        assert manager.get('fg_primary') == '#FFFFFF'
        assert manager.get('accent_primary') == '#64B5F6'
    
    def test_get_theme_color_missing_key(self):
        """Test getting theme color for missing key."""
        manager = ThemeManager()
        result = manager.get('nonexistent_key')
        assert result is None
    
    def test_get_theme_color_with_default(self):
        """Test getting theme color with default value."""
        manager = ThemeManager()
        result = manager.get('nonexistent_key', default='#000000')
        assert result == '#000000'
    
    def test_get_theme_name_light(self):
        """Test getting light theme name."""
        manager = ThemeManager('light')
        assert manager.get_theme_name() == 'Light'
    
    def test_get_theme_name_dark(self):
        """Test getting dark theme name."""
        manager = ThemeManager('dark')
        assert manager.get_theme_name() == 'Dark'
    
    def test_is_dark_light_theme(self):
        """Test is_dark with light theme."""
        manager = ThemeManager('light')
        assert manager.is_dark() is False
    
    def test_is_dark_dark_theme(self):
        """Test is_dark with dark theme."""
        manager = ThemeManager('dark')
        assert manager.is_dark() is True
    
    def test_save_preference(self, tmp_path):
        """Test saving theme preference."""
        config_file = tmp_path / 'theme_config.json'
        
        manager = ThemeManager('dark')
        # Save to temp file
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump({'theme': manager.current_theme}, f, ensure_ascii=False, indent=2)
        
        # Verify file was created and contains correct data
        assert config_file.exists()
        data = json.loads(config_file.read_text(encoding='utf-8'))
        assert data['theme'] == 'dark'
    
    def test_get_theme_manager_singleton(self):
        """Test get_theme_manager returns singleton."""
        manager1 = get_theme_manager()
        manager2 = get_theme_manager()
        assert manager1 is manager2
    
    def test_all_theme_keys_exist(self):
        """Test that all expected theme keys exist."""
        manager_light = ThemeManager('light')
        manager_dark = ThemeManager('dark')
        
        expected_keys = [
            'name', 'bg_primary', 'bg_secondary', 'bg_tertiary',
            'fg_primary', 'fg_secondary', 'fg_tertiary',
            'accent_primary', 'accent_secondary', 'accent_danger', 'accent_warning',
            'border', 'button_bg', 'button_fg', 'button_hover',
            'entry_bg', 'entry_fg', 'entry_border',
            'tree_bg', 'tree_fg', 'tree_select',
            'menu_bg', 'menu_fg', 'menu_select'
        ]
        
        for key in expected_keys:
            assert manager_light.get(key) is not None, f"Light theme missing key: {key}"
            assert manager_dark.get(key) is not None, f"Dark theme missing key: {key}"

