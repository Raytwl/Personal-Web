"""
Test script to verify all imports work correctly.
"""

import sys
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("Testing imports...")
print("=" * 60)

try:
    print("1. Testing database imports...")
    from database.db_manager import DatabaseManager
    from database.models import User, Project, Task, License, Risk
    print("   [OK] Database imports successful")
except Exception as e:
    print(f"   [FAIL] Database import failed: {e}")
    sys.exit(1)

try:
    print("2. Testing auth imports...")
    from auth.login import AuthManager
    print("   [OK] Auth imports successful")
except Exception as e:
    print(f"   [FAIL] Auth import failed: {e}")
    sys.exit(1)

try:
    print("3. Testing license imports...")
    from license.license_manager import LicenseManager
    print("   [OK] License imports successful")
except Exception as e:
    print(f"   [FAIL] License import failed: {e}")
    sys.exit(1)

try:
    print("4. Testing feature imports...")
    from features.progress_visualization import ProgressVisualizer
    from features.task_allocation import TaskAllocationManager
    from features.risk_warning import RiskWarningSystem
    print("   [OK] Feature imports successful")
except Exception as e:
    print(f"   [FAIL] Feature import failed: {e}")
    sys.exit(1)

try:
    print("5. Testing utils imports...")
    from utils.helpers import format_date, get_status_color, get_priority_color, get_severity_color
    print("   [OK] Utils imports successful")
except Exception as e:
    print(f"   [FAIL] Utils import failed: {e}")
    sys.exit(1)

try:
    print("6. Testing UI imports...")
    from ui.login_window import LoginWindow
    from ui.main_window import MainWindow
    print("   [OK] UI imports successful")
except Exception as e:
    print(f"   [FAIL] UI import failed: {e}")
    sys.exit(1)

try:
    print("7. Testing main module...")
    import main
    print("   [OK] Main module import successful")
except Exception as e:
    print(f"   [FAIL] Main module import failed: {e}")
    sys.exit(1)

print("\nAll imports successful! The application should be able to run.")
print("\nTo run the application, use: python main.py")

