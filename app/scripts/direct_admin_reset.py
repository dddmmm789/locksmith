from app import create_app, db
from app.models.admin import Admin
from werkzeug.security import generate_password_hash

def direct_reset():
    app = create_app()
    with app.app_context():
        # Delete all existing admins
        Admin.query.delete()
        db.session.commit()
        
        # Create new admin with direct password hash
        password = 'admin123'
        password_hash = generate_password_hash(password)
        
        # Create admin using raw SQL to ensure it's exactly as we want
        db.session.execute(
            """
            INSERT INTO admin (username, password_hash)
            VALUES (:username, :password_hash)
            """,
            {
                'username': 'admin',
                'password_hash': password_hash
            }
        )
        db.session.commit()
        
        # Verify
        admin = Admin.query.first()
        if admin:
            print("Admin created successfully")
            print(f"Username: admin")
            print(f"Password: {password}")
            print(f"Hash: {admin.password_hash}")
            
            # Test password verification
            if admin.check_password(password):
                print("Password verification successful!")
            else:
                print("Password verification failed!")
        else:
            print("Failed to create admin")

if __name__ == '__main__':
    direct_reset() 