from typing import Tuple, Optional

from app.auth.validators import validate_email
from app.extensions import db
from app.models.user import User
from app.utils.logger import create_log


class AuthService:
    @staticmethod
    def register_user(username: str, email: str, password: str) -> Tuple[bool, str]:
        try:

            # Validate email
            is_valid_email, email_message = validate_email(email)
            if not is_valid_email:
                return False, email_message

            if User.query.filter_by(username=username).first():
                return False, "Username already exists"

            if User.query.filter_by(email=email).first():
                return False, "Email already registered"

            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            return True, "Registration successful"
        except Exception as e:
            create_log(
                action="Registration failed",
                description=f"Failed to registration user: {str(e)}",
                status="error"
            )
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[User]]:
        try:
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                user.last_login = db.func.now()
                db.session.commit()
                return True, "Login successful", user
            return False, "Invalid username or password", None
        except Exception as e:
            return False, str(e), None