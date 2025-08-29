#!/usr/bin/env python3
"""
Theme Management System for VysualPy

Provides runtime theme switching, custom CSS loading, and style management
for the editor interface and node graph system.
"""

import os
import json
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QFont


class ThemeManager(QObject):
    """Manages theme switching and style application for VysualPy."""
    
    # Signal emitted when theme changes
    themeChanged = pyqtSignal(str)  # theme_name
    
    def __init__(self):
        super().__init__()
        self.config_dir = os.path.join(os.path.dirname(__file__), 'config')
        self.current_theme = 'dark'
        self.available_themes = ['dark', 'light', 'high_contrast']
        self.custom_styles = {}
        
        # Load theme configurations
        self.load_theme_configs()
        
        # Load current theme from config
        if hasattr(self, 'theme_config') and 'current_theme' in self.theme_config:
            self.current_theme = self.theme_config['current_theme']
        
    def load_theme_configs(self):
        """Load theme configurations from config directory."""
        theme_config_file = os.path.join(self.config_dir, 'themes.json')
        
        # Create default theme config if it doesn't exist
        if not os.path.exists(theme_config_file):
            self.create_default_theme_config()
            
        try:
            with open(theme_config_file, 'r', encoding='utf-8') as f:
                self.theme_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading theme config: {e}")
            self.theme_config = self.get_default_theme_config()
            
    def create_default_theme_config(self):
        """Create default theme configuration file."""
        default_config = self.get_default_theme_config()
        theme_config_file = os.path.join(self.config_dir, 'themes.json')
        
        try:
            with open(theme_config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4)
        except Exception as e:
            print(f"Error creating default theme config: {e}")
            
    def get_default_theme_config(self) -> Dict[str, Any]:
        """Get default theme configuration."""
        return {
            "themes": {
                "dark": {
                    "name": "Dark Theme",
                    "description": "Professional dark theme for coding",
                    "colors": {
                        "background": "#2d3748",
                        "foreground": "#e2e8f0",
                        "accent": "#4a5568",
                        "highlight": "#718096",
                        "selection": "#4a5568"
                    },
                    "fonts": {
                        "editor": {
                            "family": "Courier New",
                            "size": 11,
                            "weight": "normal"
                        },
                        "ui": {
                            "family": "Segoe UI",
                            "size": 9,
                            "weight": "normal"
                        }
                    }
                },
                "light": {
                    "name": "Light Theme",
                    "description": "Clean light theme for day work",
                    "colors": {
                        "background": "#ffffff",
                        "foreground": "#2d3748",
                        "accent": "#e2e8f0",
                        "highlight": "#bee3f8",
                        "selection": "#bee3f8"
                    },
                    "fonts": {
                        "editor": {
                            "family": "Courier New",
                            "size": 11,
                            "weight": "normal"
                        },
                        "ui": {
                            "family": "Segoe UI",
                            "size": 9,
                            "weight": "normal"
                        }
                    }
                },
                "high_contrast": {
                    "name": "High Contrast",
                    "description": "Accessibility-focused high contrast theme",
                    "colors": {
                        "background": "#000000",
                        "foreground": "#ffffff",
                        "accent": "#ffffff",
                        "highlight": "#ffff00",
                        "selection": "#ffffff"
                    },
                    "fonts": {
                        "editor": {
                            "family": "Courier New",
                            "size": 12,
                            "weight": "bold"
                        },
                        "ui": {
                            "family": "Segoe UI",
                            "size": 10,
                            "weight": "bold"
                        }
                    }
                }
            },
            "current_theme": "dark",
            "custom_css_enabled": True,
            "font_scaling": 1.0
        }
        
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names."""
        if hasattr(self, 'theme_config') and 'themes' in self.theme_config:
            return list(self.theme_config['themes'].keys())
        return self.available_themes
        
    def get_theme_info(self, theme_name: str) -> Dict[str, Any]:
        """Get theme information by name."""
        if hasattr(self, 'theme_config') and 'themes' in self.theme_config:
            return self.theme_config['themes'].get(theme_name, {})
        return {}
        
    def set_theme(self, theme_name: str) -> bool:
        """Set the current theme."""
        if theme_name not in self.get_available_themes():
            print(f"Theme '{theme_name}' not found")
            return False
            
        self.current_theme = theme_name
        self.apply_theme()
        self.themeChanged.emit(theme_name)
        
        # Save current theme to config
        if hasattr(self, 'theme_config'):
            self.theme_config['current_theme'] = theme_name
            self.save_theme_config()
            
        return True
        
    def apply_theme(self):
        """Apply the current theme to the application."""
        css_content = self.load_theme_css()
        if css_content:
            app = QApplication.instance()
            if app:
                app.setStyleSheet(css_content)
                
    def load_theme_css(self) -> str:
        """Load CSS content for current theme."""
        css_file = os.path.join(self.config_dir, 'editor_style.css')
        
        if not os.path.exists(css_file):
            return ""
            
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                css_content = f.read()
                
            # Apply theme-specific modifications
            css_content = self.customize_css_for_theme(css_content)
            
            return css_content
            
        except Exception as e:
            print(f"Error loading CSS file: {e}")
            return ""
            
    def customize_css_for_theme(self, css_content: str) -> str:
        """Customize CSS content based on current theme."""
        theme_info = self.get_theme_info(self.current_theme)
        
        if not theme_info or 'colors' not in theme_info:
            return css_content
            
        # Replace color variables based on theme
        colors = theme_info['colors']
        
        # Simple color replacement - in a production system, you'd want
        # more sophisticated CSS variable replacement
        replacements = {
            '#2d3748': colors.get('background', '#2d3748'),
            '#e2e8f0': colors.get('foreground', '#e2e8f0'),
            '#4a5568': colors.get('accent', '#4a5568'),
            '#718096': colors.get('highlight', '#718096'),
        }
        
        for old_color, new_color in replacements.items():
            css_content = css_content.replace(old_color, new_color)
            
        return css_content
        
    def get_editor_font(self) -> QFont:
        """Get the font configuration for the editor."""
        theme_info = self.get_theme_info(self.current_theme)
        
        if theme_info and 'fonts' in theme_info and 'editor' in theme_info['fonts']:
            font_info = theme_info['fonts']['editor']
            font = QFont(font_info.get('family', 'Courier New'))
            font.setPointSize(int(font_info.get('size', 11)))
            
            weight = font_info.get('weight', 'normal')
            if weight == 'bold':
                font.setBold(True)
                
            return font
            
        # Default font
        return QFont('Courier New', 11)
        
    def get_ui_font(self) -> QFont:
        """Get the font configuration for UI elements."""
        theme_info = self.get_theme_info(self.current_theme)
        
        if theme_info and 'fonts' in theme_info and 'ui' in theme_info['fonts']:
            font_info = theme_info['fonts']['ui']
            font = QFont(font_info.get('family', 'Segoe UI'))
            font.setPointSize(int(font_info.get('size', 9)))
            
            weight = font_info.get('weight', 'normal')
            if weight == 'bold':
                font.setBold(True)
                
            return font
            
        # Default font
        return QFont('Segoe UI', 9)
        
    def add_custom_style(self, widget_name: str, css_rules: str):
        """Add custom CSS rules for specific widgets."""
        self.custom_styles[widget_name] = css_rules
        self.apply_theme()  # Re-apply theme with custom styles
        
    def remove_custom_style(self, widget_name: str):
        """Remove custom CSS rules for a widget."""
        if widget_name in self.custom_styles:
            del self.custom_styles[widget_name]
            self.apply_theme()  # Re-apply theme without custom styles
            
    def get_theme_colors(self) -> Dict[str, str]:
        """Get color palette for current theme."""
        theme_info = self.get_theme_info(self.current_theme)
        return theme_info.get('colors', {})
        
        
    def save_theme_config(self):
        """Save current theme configuration to file."""
        theme_config_file = os.path.join(self.config_dir, 'themes.json')
        
        try:
            with open(theme_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.theme_config, f, indent=4)
        except Exception as e:
            print(f"Error saving theme config: {e}")
            
    def create_custom_theme(self, theme_name: str, theme_data: Dict[str, Any]) -> bool:
        """Create a new custom theme."""
        if not hasattr(self, 'theme_config'):
            self.theme_config = self.get_default_theme_config()
            
        if 'themes' not in self.theme_config:
            self.theme_config['themes'] = {}
            
        self.theme_config['themes'][theme_name] = theme_data
        self.save_theme_config()
        
        return True
        
    def delete_custom_theme(self, theme_name: str) -> bool:
        """Delete a custom theme (cannot delete built-in themes)."""
        builtin_themes = ['dark', 'light', 'high_contrast']
        
        if theme_name in builtin_themes:
            print(f"Cannot delete built-in theme: {theme_name}")
            return False
            
        if hasattr(self, 'theme_config') and 'themes' in self.theme_config:
            if theme_name in self.theme_config['themes']:
                del self.theme_config['themes'][theme_name]
                self.save_theme_config()
                
                # Switch to default theme if we deleted the current theme
                if self.current_theme == theme_name:
                    self.set_theme('dark')
                    
                return True
                
        return False


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return theme_manager


def apply_theme_to_widget(widget, theme_colors: Optional[Dict[str, str]] = None):
    """Apply current theme colors to a specific widget."""
    if theme_colors is None:
        theme_colors = theme_manager.get_theme_colors()
        
    if not theme_colors:
        return
        
    # Apply basic styling based on theme colors
    style = f"""
    QWidget {{
        background-color: {theme_colors.get('background', '#2d3748')};
        color: {theme_colors.get('foreground', '#e2e8f0')};
    }}
    """
    
    widget.setStyleSheet(style)


if __name__ == "__main__":
    # Test the theme manager
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Theme Manager Test")
    
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    text_edit = QTextEdit()
    text_edit.setText("This is a test of the theme system.\nColors should change when theme is switched.")
    layout.addWidget(text_edit)
    
    window.setCentralWidget(central_widget)
    
    # Apply initial theme
    theme_manager.apply_theme()
    
    # Show window
    window.show()
    
    print(f"Available themes: {theme_manager.get_available_themes()}")
    print(f"Current theme: {theme_manager.current_theme}")
    
    app.exec_()
