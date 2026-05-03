"""
Authentication module for TeamAxis.
"""

from database.db_manager import DatabaseManager
from license.license_manager import LicenseManager

class AuthManager:
    """Manages user authentication."""
    
    def __init__(self):
        """Initialize authentication manager."""
        self.db_manager = DatabaseManager()
        self.license_manager = LicenseManager()
        self.current_user = None
    
    def login(self, username, password, license_key=None):
        """Authenticate user with username, password and license key."""
        # First authenticate user
        user = self.db_manager.authenticate_user(username, password)
        if not user:
            return False, "Invalid username or password"
        
        # Check license if provided
        if license_key:
            license_key = license_key.strip().replace(' ', '')
            is_valid, message = self.license_manager.check_license_validity(license_key)
            if not is_valid:
                return False, f"License validation failed: {message}"
            
            # Check if license is assigned to this user
            license_obj = self.license_manager.get_license_by_key(license_key)
            if license_obj and license_obj.user_id != user.user_id:
                return False, "License does not belong to this user"
        
        # If admin user, allow login without license check
        if user.role == 'admin':
            self.current_user = user
            return True, "Login successful"
        
        # For regular users, license is required
        if not license_key:
            return False, "License key is required for login"
        
        self.current_user = user
        return True, "Login successful"
    
    def register(self, username, password, email, license_key):
        """Register a new user with license validation."""
        # Validate license first
        if not license_key:
            return False, "License key is required for registration"
        
        license_key = license_key.strip().replace(' ', '')
        
        # Check if license exists and is valid
        license_obj = self.license_manager.get_license_by_key(license_key)
        if not license_obj:
            return False, "License key not found"
        
        # Check if license is already assigned to another user
        if license_obj.user_id:
            return False, "License is already assigned to another user"
        
        # Check license validity
        is_valid, message = self.license_manager.check_license_validity(license_key)
        if not is_valid:
            return False, f"Invalid license: {message}"
        
        # Create user
        user_id = self.db_manager.create_user(username, password, email, 'user')
        if not user_id:
            return False, "Username already exists"
        
        # Assign license to user
        self.db_manager.assign_license_to_user(license_obj.license_id, user_id)
        
        return True, "Registration successful"
    
    def logout(self):
        """Logout current user."""
        self.current_user = None
    
    def is_authenticated(self):
        """Check if user is authenticated."""
        return self.current_user is not None
    
    def get_current_user(self):
        """Get current authenticated user."""
        return self.current_user
    
    def is_admin(self):
        """Check if current user is admin."""
        return self.current_user and self.current_user.role == 'admin'

