from app.extensions import db
from app.models.log import Log
from flask_login import current_user

def create_log(action, description, status="success"):
    try:
        log = Log(
            action=action,
            description=description,
            user_id=current_user.id if not current_user.is_anonymous else None,
            status=status
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error creating log: {e}")
        db.session.rollback()