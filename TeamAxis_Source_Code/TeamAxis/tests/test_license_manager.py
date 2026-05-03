"""
Tests for license/license_manager.py
"""

import pytest
from datetime import datetime, timedelta
from license.license_manager import LicenseManager

class TestLicenseManager:
    """Test LicenseManager class."""
    
    def test_generate_license_key(self, license_manager):
        """Test license key generation."""
        key = license_manager.generate_license_key()
        assert key is not None
        assert len(key) == 19  # XXXX-XXXX-XXXX-XXXX format
        assert key.count('-') == 3
        assert all(c.isalnum() or c == '-' for c in key)
    
    def test_generate_license_key_unique(self, license_manager):
        """Test that generated license keys are unique."""
        keys = [license_manager.generate_license_key() for _ in range(10)]
        assert len(keys) == len(set(keys))  # All unique
    
    def test_format_license_key_valid(self, license_manager):
        """Test formatting valid license key."""
        key = 'ABCD1234EFGH5678'
        formatted = license_manager.format_license_key(key)
        assert formatted == 'ABCD-1234-EFGH-5678'
    
    def test_format_license_key_with_dashes(self, license_manager):
        """Test formatting license key that already has dashes."""
        key = 'ABCD-1234-EFGH-5678'
        formatted = license_manager.format_license_key(key)
        assert formatted == 'ABCD-1234-EFGH-5678'
    
    def test_format_license_key_with_spaces(self, license_manager):
        """Test formatting license key with spaces."""
        key = 'ABCD 1234 EFGH 5678'
        formatted = license_manager.format_license_key(key)
        assert formatted == 'ABCD-1234-EFGH-5678'
    
    def test_format_license_key_lowercase(self, license_manager):
        """Test formatting lowercase license key."""
        key = 'abcd1234efgh5678'
        formatted = license_manager.format_license_key(key)
        assert formatted == 'ABCD-1234-EFGH-5678'
    
    def test_format_license_key_invalid_length(self, license_manager):
        """Test formatting license key with invalid length."""
        key = 'SHORT'
        formatted = license_manager.format_license_key(key)
        assert formatted == key  # Returns as-is if invalid
    
    def test_create_license(self, license_manager, sample_user):
        """Test creating a license."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        assert license_id is not None
        assert license_key is not None
        assert len(license_key) == 19
    
    def test_create_license_custom_days(self, license_manager, sample_user):
        """Test creating license with custom validity days."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 30)
        
        licenses = license_manager.get_all_licenses()
        license_obj = next(l for l in licenses if l.license_id == license_id)
        
        issue_date = datetime.strptime(license_obj.issue_date, '%Y-%m-%d').date()
        expiry_date = datetime.strptime(license_obj.expiry_date, '%Y-%m-%d').date()
        
        assert (expiry_date - issue_date).days == 30
    
    def test_get_all_licenses(self, license_manager, sample_user):
        """Test getting all licenses."""
        license_manager.create_license(sample_user.user_id, 365)
        license_manager.create_license(None, 180)
        
        licenses = license_manager.get_all_licenses()
        assert len(licenses) >= 2
    
    def test_get_license_by_user(self, license_manager, sample_user):
        """Test getting license by user."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        
        user_licenses = license_manager.get_license_by_user(sample_user.user_id)
        assert len(user_licenses) >= 1
        assert any(l.license_id == license_id for l in user_licenses)
    
    def test_get_license_by_user_no_license(self, license_manager, sample_user):
        """Test getting license for user without license."""
        user_licenses = license_manager.get_license_by_user(sample_user.user_id)
        assert len(user_licenses) == 0
    
    def test_check_license_validity_valid(self, license_manager, sample_user):
        """Test checking valid license."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        
        is_valid, message = license_manager.check_license_validity(license_key)
        assert is_valid is True
        assert 'valid' in message.lower()
    
    def test_check_license_validity_expired(self, license_manager, sample_user):
        """Test checking expired license."""
        # Create expired license
        license_key = license_manager.generate_license_key()
        issue_date = (datetime.now() - timedelta(days=400)).date()
        expiry_date = (datetime.now() - timedelta(days=30)).date()
        
        license_id = license_manager.db_manager.create_license(
            license_key, sample_user.user_id, issue_date, expiry_date, 'active'
        )
        
        is_valid, message = license_manager.check_license_validity(license_key)
        assert is_valid is False
        assert 'expired' in message.lower()
    
    def test_check_license_validity_revoked(self, license_manager, sample_user):
        """Test checking revoked license."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        license_manager.revoke_license(license_id)
        
        is_valid, message = license_manager.check_license_validity(license_key)
        assert is_valid is False
        assert 'revoked' in message.lower()
    
    def test_check_license_validity_not_found(self, license_manager):
        """Test checking non-existent license."""
        is_valid, message = license_manager.check_license_validity('NONEXISTENT-KEY-1234')
        assert is_valid is False
        assert 'not found' in message.lower()
    
    def test_check_license_validity_without_dashes(self, license_manager, sample_user):
        """Test checking license validity with key without dashes."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        key_without_dashes = license_key.replace('-', '')
        
        is_valid, message = license_manager.check_license_validity(key_without_dashes)
        assert is_valid is True
    
    def test_get_license_by_key(self, license_manager, sample_user):
        """Test getting license by key."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        
        license_obj = license_manager.get_license_by_key(license_key)
        assert license_obj is not None
        assert license_obj.license_id == license_id
    
    def test_get_license_by_key_not_found(self, license_manager):
        """Test getting non-existent license by key."""
        license_obj = license_manager.get_license_by_key('NONEXISTENT-KEY-1234')
        assert license_obj is None
    
    def test_revoke_license(self, license_manager, sample_user):
        """Test revoking a license."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        license_manager.revoke_license(license_id)
        
        licenses = license_manager.get_all_licenses()
        revoked_license = next(l for l in licenses if l.license_id == license_id)
        assert revoked_license.status == 'revoked'
    
    def test_activate_license(self, license_manager, sample_user):
        """Test activating a license."""
        license_id, license_key = license_manager.create_license(sample_user.user_id, 365)
        license_manager.revoke_license(license_id)
        license_manager.activate_license(license_id)
        
        licenses = license_manager.get_all_licenses()
        activated_license = next(l for l in licenses if l.license_id == license_id)
        assert activated_license.status == 'active'
    
    def test_get_expiring_licenses(self, license_manager, sample_user):
        """Test getting expiring licenses."""
        # Create license expiring in 20 days
        license_key = license_manager.generate_license_key()
        issue_date = datetime.now().date()
        expiry_date = issue_date + timedelta(days=20)
        
        license_id = license_manager.db_manager.create_license(
            license_key, sample_user.user_id, issue_date, expiry_date, 'active'
        )
        
        expiring = license_manager.get_expiring_licenses(30)
        assert len(expiring) >= 1
        assert any(l.license_id == license_id for l in expiring)
    
    def test_get_expiring_licenses_not_expiring(self, license_manager, sample_user):
        """Test getting expiring licenses when none are expiring."""
        # Create license expiring in 60 days
        license_key = license_manager.generate_license_key()
        issue_date = datetime.now().date()
        expiry_date = issue_date + timedelta(days=60)
        
        license_manager.db_manager.create_license(
            license_key, sample_user.user_id, issue_date, expiry_date, 'active'
        )
        
        expiring = license_manager.get_expiring_licenses(30)
        assert not any(l.license_key == license_key for l in expiring)

