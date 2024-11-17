from flask import Flask, render_template
import logging


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Register blueprints
    from app.vms.routes import vm_bp
    # app.register_blueprint(vm_bp)
    # app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(vm_bp, url_prefix='/vms')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app
