"""
License management module for TeamAxis.
"""

import uuid
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager

class LicenseManager:
    """Manages software licenses."""
    
    def __init__(self):
        """Initialize license manager."""
        self.db_manager = DatabaseManager()
    
    def generate_license_key(self):
        """Generate a unique license key in format XXXX-XXXX-XXXX-XXXX."""
        key = str(uuid.uuid4()).replace('-', '').upper()[:16]
        # Format as XXXX-XXXX-XXXX-XXXX
        return f"{key[0:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"
    
    def format_license_key(self, license_key):
        """Format license key to XXXX-XXXX-XXXX-XXXX format."""
        # Remove any existing dashes and spaces
        key = license_key.replace('-', '').replace(' ', '').upper()
        if len(key) == 16:
            return f"{key[0:4]}-{key[4:8]}-{key[8:12]}-{key[12:16]}"
        return license_key
    
    def create_license(self, user_id, days_valid=365):
        """Create a new license for a user."""
        license_key = self.generate_license_key()
        issue_date = datetime.now().date()
        expiry_date = issue_date + timedelta(days=days_valid)
        
        license_id = self.db_manager.create_license(
            license_key, user_id, issue_date, expiry_date, 'active'
        )
        return license_id, license_key
    
    def get_all_licenses(self):
        """Get all licenses."""
        return self.db_manager.get_all_licenses()
    
    def get_license_by_user(self, user_id):
        """Get license for a specific user."""
        licenses = self.get_all_licenses()
        return [lic for lic in licenses if lic.user_id == user_id]
    
    def check_license_validity(self, license_key):
        """Check if a license is valid."""
        # Format the license key
        formatted_key = self.format_license_key(license_key)
        licenses = self.get_all_licenses()
        for license in licenses:
            # Compare both formatted versions (with and without dashes)
            license_key_clean = license.license_key.replace('-', '').upper()
            input_key_clean = license_key.replace('-', '').replace(' ', '').upper()
            
            if license.license_key == formatted_key or license_key_clean == input_key_clean:
                if license.status == 'active':
                    expiry = datetime.strptime(license.expiry_date, '%Y-%m-%d').date()
                    if expiry >= datetime.now().date():
                        return True, "License valid"
                    else:
                        return False, "License expired"
                else:
                    return False, "License revoked"
        return False, "License not found"
    
    def get_license_by_key(self, license_key):
        """Get license by license key."""
        formatted_key = self.format_license_key(license_key)
        licenses = self.get_all_licenses()
        input_key_clean = license_key.replace('-', '').replace(' ', '').upper()
        
        for license in licenses:
            license_key_clean = license.license_key.replace('-', '').upper()
            if license.license_key == formatted_key or license_key_clean == input_key_clean:
                return license
        return None
    
    def revoke_license(self, license_id):
        """Revoke a license."""
        self.db_manager.update_license_status(license_id, 'revoked')
    
    def activate_license(self, license_id):
        """Activate a license."""
        self.db_manager.update_license_status(license_id, 'active')
    
    def get_expiring_licenses(self, days_ahead=30):
        """Get licenses expiring within specified days."""
        licenses = self.get_all_licenses()
        expiring = []
        today = datetime.now().date()
        threshold = today + timedelta(days=days_ahead)
        
        for license in licenses:
            if license.status == 'active':
                expiry = datetime.strptime(license.expiry_date, '%Y-%m-%d').date()
                if today <= expiry <= threshold:
                    expiring.append(license)
        return expiring

