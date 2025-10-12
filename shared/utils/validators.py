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

def validate_otp(otp):
    """Validate OTP format"""
    if not otp or not isinstance(otp, str):
        return False, "OTP is required"

    if not otp.isdigit():
        return False, "OTP must contain only digits"

    if len(otp) != 6:
        return False, "OTP must be exactly 6 digits"

    return True, "OTP is valid"

def validate_subject_name(subject_name):
    """Validate subject name"""
    if not subject_name or not isinstance(subject_name, str):
        return False, "Subject name is required"

    subject_name = subject_name.strip()
    if len(subject_name) < 2:
        return False, "Subject name must be at least 2 characters long"

    if len(subject_name) > 100:
        return False, "Subject name must be less than 100 characters"

    return True, "Subject name is valid"

def validate_course_name(course_name):
    """Validate course name"""
    if not course_name or not isinstance(course_name, str):
        return False, "Course name is required"

    course_name = course_name.strip()
    if len(course_name) < 2:
        return False, "Course name must be at least 2 characters long"

    if len(course_name) > 100:
        return False, "Course name must be less than 100 characters"

    return True, "Course name is valid"

def validate_price(price):
    """Validate price value"""
    try:
        price_float = float(price)
        if price_float < 0:
            return False, "Price cannot be negative"
        if price_float > 999999.99:
            return False, "Price is too high"
        return True, "Price is valid"
    except (ValueError, TypeError):
        return False, "Price must be a valid number"

def validate_token_count(tokens):
    """Validate token count"""
    try:
        token_int = int(tokens)
        if token_int < 0:
            return False, "Token count cannot be negative"
        if token_int > 1000000:
            return False, "Token count is too high"
        return True, "Token count is valid"
    except (ValueError, TypeError):
        return False, "Token count must be a valid integer"

def validate_mock_test_count(count):
    """Validate mock test count"""
    try:
        count_int = int(count)
        if count_int < 1:
            return False, "Mock test count must be at least 1"
        if count_int > 1000:
            return False, "Mock test count cannot exceed 1000"
        return True, "Mock test count is valid"
    except (ValueError, TypeError):
        return False, "Mock test count must be a valid integer"

def validate_blog_title(title):
    """Validate blog post title"""
    if not title or not isinstance(title, str):
        return False, "Title is required"

    title = title.strip()
    if len(title) < 5:
        return False, "Title must be at least 5 characters long"

    if len(title) > 255:
        return False, "Title must be less than 255 characters"

    return True, "Title is valid"

def validate_blog_content(content):
    """Validate blog post content"""
    if not content or not isinstance(content, str):
        return False, "Content is required"

    content = content.strip()
    if len(content) < 10:
        return False, "Content must be at least 10 characters long"

    if len(content) > 10000:
        return False, "Content must be less than 10,000 characters"

    return True, "Content is valid"

def validate_tags(tags):
    """Validate tags string"""
    if not tags:
        return True, "Tags are optional"

    if not isinstance(tags, str):
        return False, "Tags must be a string"

    if len(tags) > 500:
        return False, "Tags must be less than 500 characters"

    return True, "Tags are valid"
