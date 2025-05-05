# utils/validators.py
import re
from typing import Optional, Dict, Any

def validate_email(email: str) -> bool:
    """
    Validate email address format
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_password(password: str) -> bool:
    """
    Validate password strength
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one number
    """
    return (
        len(password) >= 8 and
        any(c.isupper() for c in password) and
        any(c.islower() for c in password) and
        any(c.isdigit() for c in password)
    )

def validate_registration(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate user registration data
    """
    if not data:
        return "No registration data provided"
    
    # Check email
    email = data.get('email')
    if not email:
        return "Email is required"
    if not validate_email(email):
        return "Invalid email format"
    
    # Check password
    password = data.get('password')
    if not password:
        return "Password is required"
    if not validate_password(password):
        return "Password must be at least 8 characters long and contain uppercase, lowercase, and numbers"
    
    return None

def validate_login(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate user login data
    """
    if not data:
        return "No login data provided"
    
    # Check email
    email = data.get('email')
    if not email:
        return "Email is required"
    if not validate_email(email):
        return "Invalid email format"
    
    # Check password
    password = data.get('password')
    if not password:
        return "Password is required"
    
    return None

def validate_user_profile(data: Dict[str, Any]) -> Optional[str]:
    """
    Validate user profile update data
    """
    if not data:
        return "No profile data provided"
    
    # Optional name validation
    name = data.get('name')
    if name and (len(name) < 2 or len(name) > 50):
        return "Name must be between 2 and 50 characters"
    
    # Birth details validation
    birth_details = data.get('birth_details', {})
    if birth_details:
        # Validate date
        date = birth_details.get('date')
        if not date:
            return "Birth date is required"
        
        # Validate time
        time = birth_details.get('time')
        if not time:
            return "Birth time is required"
        
        # Validate place
        place = birth_details.get('place')
        if not place:
            return "Birth place is required"
    
    return None