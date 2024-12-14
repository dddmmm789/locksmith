from app import create_app, db
from app.models.admin import Admin
import os

def force_reset_admin():
    app = create_app()
    with app.app_context():
        # Drop and recreate admin table
        db.session.execute('DROP TABLE IF EXISTS admin')
        db.session.commit()
        
        # Create admin table
        db.create_all()
        
        # Create new admin user
        admin = Admin(username='admin')
        admin.set_password('password')
        db.session.add(admin)
        db.session.commit()
        
        # Verify the admin was created
        admin = Admin.query.filter_by(username='admin').first()
        if admin and admin.check_password('password'):
            print("Admin user created successfully")
            print("Username: admin")
            print("Password: password")
        else:
            print("Failed to create admin user")

if __name__ == '__main__':
    force_reset_admin() 