from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config
from .extensions import db

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to ensure they're known to Flask-Migrate
    from .models import job, locksmith, review
    
    # Register blueprints
    from .routes import locksmith_routes, customer_routes, admin_routes
    app.register_blueprint(locksmith_routes.bp)
    app.register_blueprint(customer_routes.bp)
    app.register_blueprint(admin_routes.bp)
    
    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('locksmith.login'))
    
    return app
