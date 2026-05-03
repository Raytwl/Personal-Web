"""
Script to create a test license for TeamAxis.
Run this script to generate a test license key that can be used for registration and login.
"""

from database.db_manager import DatabaseManager
from license.license_manager import LicenseManager
from datetime import datetime, timedelta

def create_test_license():
    """Create a test license without assigning it to any user."""
    db_manager = DatabaseManager()
    license_manager = LicenseManager()
    
    # Generate a license key
    license_key = license_manager.generate_license_key()
    
    # Create license without user assignment (user_id = None)
    issue_date = datetime.now().date()
    expiry_date = issue_date + timedelta(days=365)  # Valid for 1 year
    
    license_id = db_manager.create_license(
        license_key, None, issue_date, expiry_date, 'active'
    )
    
    if license_id:
        print("=" * 60)
        print("TEST LICENSE CREATED SUCCESSFULLY!")
        print("=" * 60)
        print(f"\nLicense Key: {license_key}")
        print(f"Issue Date: {issue_date}")
        print(f"Expiry Date: {expiry_date}")
        print(f"Status: active")
        print(f"\nYou can use this license key to:")
        print("  1. Register a new user account")
        print("  2. Login with a registered user account")
        print("\n" + "=" * 60)
        return license_key
    else:
        print("Failed to create license. It may already exist.")
        return None

if __name__ == "__main__":
    create_test_license()

