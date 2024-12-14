from app import create_app, db
app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    # Create all tables with the new schema
    db.create_all() 