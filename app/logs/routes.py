from flask import Blueprint, render_template
from flask_login import login_required
from app.models.log import Log

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/logs')
@login_required
def view_logs():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template('logs/list.html', logs=logs)
