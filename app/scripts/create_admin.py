from app import create_app, db
from app.models.admin import Admin

def create_admin_user(username, password):
    app = create_app()
    with app.app_context():
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            print(f"Admin user '{username}' already exists")
            return
        
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python create_admin.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    create_admin_user(username, password) 