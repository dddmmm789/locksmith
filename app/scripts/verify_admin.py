from app import create_app, db
from app.models.admin import Admin
from werkzeug.security import generate_password_hash, check_password_hash

def verify_admin():
    app = create_app()
    with app.app_context():
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            print("No admin user found")
            return
        
        print(f"Admin ID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Password hash exists: {bool(admin.password_hash)}")
        
        # Test password verification
        test_password = 'password'
        result = admin.check_password(test_password)
        print(f"Password verification test: {'Success' if result else 'Failed'}")
        
        # Create new password hash for comparison
        new_hash = generate_password_hash(test_password)
        print(f"Stored hash: {admin.password_hash}")
        print(f"New hash: {new_hash}")

if __name__ == '__main__':
    verify_admin() 