import sentry_sdk
from sentry_sdk import capture_event
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
    # sentry_sdk.init(
    #     dsn="https://0129a3f3edc7b0e1efc8cccd2092d873@o4508399358312448.ingest.de.sentry.io/4508399366176848",
    #     # Set traces_sample_rate to 1.0 to capture 100%
    #     # of transactions for tracing.
    #     traces_sample_rate=1.0,
    #     _experiments={
    #         # Set continuous_profiling_auto_start to True
    #         # to automatically start the profiler on when
    #         # possible.
    #         "continuous_profiling_auto_start": True,
    #     },
    # )

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Register blueprints
    from app.vms.routes import vm_bp
    from app.auth.routes import auth_bp
    from app.logs.routes import logs_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(vm_bp, url_prefix='/vms')
    app.register_blueprint(logs_bp, url_prefix='/logs')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
