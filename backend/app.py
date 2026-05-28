"""
Main Application — Flask Entry Point
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
try:
    from flask_jwt_extended import JWTManager  # type: ignore[import]
    jwt = JWTManager()
except ImportError:
    JWTManager = None
    jwt = None

# Configuration
from config import config

# Database
from utils.db import init_db
from models.user import db

# Mail
from utils.email import init_mail

# Blueprints
from routes.auth_routes import auth_bp
from routes.fees_routes import fees_bp
from routes.payment_routes import payments_bp
from routes.admin_routes import admin_bp


def create_app(config_name=None):
    """Create and configure Flask application"""
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config.get(config_name, config['development']))
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    init_mail(app)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(fees_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(admin_bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({'error': 'Server error'}), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'service': 'Njala University Fees Management System',
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'Njala University Fees Management System',
            'endpoints': {
                'auth': '/api/auth',
                'fees': '/api/fees',
                'payments': '/api/payments',
                'admin': '/api/admin'
            }
        }), 200
    
    # Database initialization
    with app.app_context():
        init_db(app)
        print('✓ Application initialized successfully')
    
    return app


# Application entry point
if __name__ == '__main__':
    app = create_app()
    
    # Development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
