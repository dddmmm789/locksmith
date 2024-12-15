from app import create_app, db
from app.models.admin import Admin

def reset_admin():
    app = create_app()
    with app.app_context():
        # Delete existing admin users
        Admin.query.delete()
        db.session.commit()
        
        # Create new admin user with simple password
        admin = Admin(username='admin')
        admin.set_password('password')  # Simpler password for testing
        db.session.add(admin)
        db.session.commit()
        print("Admin user reset successfully")
        print("Username: admin")
        print("Password: password")

if __name__ == '__main__':
    reset_admin() 