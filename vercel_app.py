# vercel_app.py
from flask import Flask, jsonify, render_template
from app import create_app
from app.extensions import db
from app.models.user import User
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = create_app()


# Error handlers with better error pages
@app.errorhandler(500)
def handle_500_error(error):
    logger.error(f'Server Error: {error}')
    if app.debug:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(error)
        }), 500
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def handle_404_error(error):
    logger.error(f'Page Not Found: {error}')
    return render_template('errors/404.html'), 404


# Health check route for Vercel
@app.route('/health')
def health_check():
    try:
        # Test database connection
        with app.app_context():
            db.session.execute('SELECT 1')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'environment': os.getenv('FLASK_ENV', 'production')
        })
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# Debug route (only available in development)
@app.route('/debug')
def debug():
    if not app.debug:
        return jsonify({'error': 'Debug endpoint not available in production'}), 403

    return jsonify({
        'status': 'ok',
        'environment': os.getenv('FLASK_ENV', 'production'),
        'debug': app.debug,
        'database_url': os.getenv('DATABASE_URL', 'not_set')[:8] + '...',  # Show only start of URL
        'blueprints': list(app.blueprints.keys()),
        'routes': [str(rule) for rule in app.url_map.iter_rules()]
    })


# Initialize database
with app.app_context():
    try:
        db.create_all()
        # Create admin user if doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username=os.getenv('ADMIN_USERNAME', 'admin'),
                email=os.getenv('ADMIN_EMAIL', 'admin@example.com')
            )
            admin.set_password(os.getenv('ADMIN_PASSWORD', 'admin123'))
            db.session.add(admin)
            db.session.commit()
            logger.info('Admin user created successfully')
    except Exception as e:
        logger.error(f'Database initialization error: {e}')
        # In production, you might want to raise the error
        if not app.debug:
            raise e

# Required for Vercel
app = app.wsgi_app