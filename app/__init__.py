from flask import Flask, render_template
import logging
from app.config import Config
from app.extensions import db, login_manager

login_manager.login_view = 'auth.login'  # Where to redirect if not logged in


@login_manager.user_loader
def load_user(id):
    from app.models.user import User
    return User.query.get(int(id))


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Register blueprints
    from app.vms.routes import vm_bp
    from app.auth.routes import auth_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vm_bp, url_prefix='/vms')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
