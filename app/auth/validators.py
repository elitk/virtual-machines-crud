from typing import Tuple

def validate_password(password: str) -> Tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def validate_email(email: str) -> Tuple[bool, str]:
    if not '@' in email:
        return False, "Invalid email format"
    return True, "Email is valid"