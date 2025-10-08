import re

def validate_email_format(email):
    """Validate email format using regex"""
    if not email or not isinstance(email, str):
        return False

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_mobile_number(mobile):
    """Validate mobile number format (Indian format)"""
    pattern = r'^[6-9]\d{9}$'
    return bool(re.match(pattern, mobile))

def validate_password_strength(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def validate_name(name):
    """Validate name format"""
    if len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    if not re.match(r'^[a-zA-Z\s]+$', name.strip()):
        return False, "Name can only contain letters and spaces"
    
    return True, "Name is valid"
