from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .extensions import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from .routes import locksmith_routes, customer_routes, admin_routes
    app.register_blueprint(locksmith_routes.bp)
    app.register_blueprint(customer_routes.bp)
    app.register_blueprint(admin_routes.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
