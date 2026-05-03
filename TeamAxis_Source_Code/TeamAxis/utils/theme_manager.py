"""
Theme manager for TeamAxis.
Supports Light and Dark themes.
"""

import json
import os

class ThemeManager:
    """Manages application themes."""
    
    # Theme color schemes
    THEMES = {
        'light': {
            'name': 'Light',
            'bg_primary': '#FFFFFF',
            'bg_secondary': '#F5F5F5',
            'bg_tertiary': '#E0E0E0',
            'fg_primary': '#000000',
            'fg_secondary': '#333333',
            'fg_tertiary': '#666666',
            'accent_primary': '#2196F3',
            'accent_secondary': '#4CAF50',
            'accent_danger': '#F44336',
            'accent_warning': '#FF9800',
            'border': '#CCCCCC',
            'button_bg': '#2196F3',
            'button_fg': '#FFFFFF',
            'button_hover': '#1976D2',
            'entry_bg': '#FFFFFF',
            'entry_fg': '#000000',
            'entry_border': '#CCCCCC',
            'tree_bg': '#FFFFFF',
            'tree_fg': '#000000',
            'tree_select': '#E3F2FD',
            'menu_bg': '#FFFFFF',
            'menu_fg': '#000000',
            'menu_select': '#E3F2FD',
        },
        'dark': {
            'name': 'Dark',
            'bg_primary': '#1E1E1E',
            'bg_secondary': '#2D2D2D',
            'bg_tertiary': '#3D3D3D',
            'fg_primary': '#FFFFFF',
            'fg_secondary': '#E0E0E0',
            'fg_tertiary': '#B0B0B0',
            'accent_primary': '#64B5F6',
            'accent_secondary': '#81C784',
            'accent_danger': '#E57373',
            'accent_warning': '#FFB74D',
            'border': '#555555',
            'button_bg': '#64B5F6',
            'button_fg': '#FFFFFF',
            'button_hover': '#42A5F5',
            'entry_bg': '#2D2D2D',
            'entry_fg': '#FFFFFF',
            'entry_border': '#555555',
            'tree_bg': '#2D2D2D',
            'tree_fg': '#FFFFFF',
            'tree_select': '#424242',
            'menu_bg': '#2D2D2D',
            'menu_fg': '#FFFFFF',
            'menu_select': '#424242',
        }
    }
    
    def __init__(self, default_theme='light'):
        """Initialize theme manager."""
        self.current_theme = default_theme
        self.load_preference()
    
    def load_preference(self):
        """Load theme preference from file."""
        config_file = 'theme_config.json'
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    theme = config.get('theme', 'light')
                    if theme in self.THEMES:
                        self.current_theme = theme
            except:
                pass  # Use default if file is corrupted
    
    def save_preference(self):
        """Save theme preference to file."""
        config_file = 'theme_config.json'
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({'theme': self.current_theme}, f, ensure_ascii=False, indent=2)
        except:
            pass  # Ignore save errors
    
    def set_theme(self, theme):
        """Set current theme."""
        if theme in self.THEMES:
            self.current_theme = theme
            self.save_preference()
            return True
        return False
    
    def get(self, key, default=None):
        """Get theme color value."""
        return self.THEMES.get(self.current_theme, {}).get(key, default)
    
    def get_theme_name(self):
        """Get current theme name."""
        return self.THEMES.get(self.current_theme, {}).get('name', 'Light')
    
    def is_dark(self):
        """Check if current theme is dark."""
        return self.current_theme == 'dark'

# Global theme manager instance
_theme_manager = None

def get_theme_manager():
    """Get global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager

