"""
TeamAxis - Project Management System
Main entry point for the application.
"""

import warnings
import os
import logging

# Suppress warnings before importing other modules
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*iCCP.*')
warnings.filterwarnings('ignore', message='.*Tight layout.*')

# Suppress PNG warnings from PIL/Pillow
os.environ['PYTHONWARNINGS'] = 'ignore'

# Suppress PIL/Pillow libpng warnings
logging.getLogger('PIL').setLevel(logging.ERROR)

from ui.login_window import LoginWindow

def on_login_success(auth_manager):
    """Callback function when login is successful."""
    from ui.main_window import MainWindow
    main_window = MainWindow(auth_manager)
    main_window.run()

if __name__ == "__main__":
    print("Starting TeamAxis application...")
    print("Initializing login window...")
    try:
        # Create and run login window
        login_window = LoginWindow(on_login_success)
        print("Login window created successfully. Starting main loop...")
        login_window.run()
        print("Application closed.")
    except Exception as e:
        print(f"ERROR: Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

