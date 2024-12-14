from app import create_app, db
from app.models.admin import Admin

def check_admin():
    app = create_app()
    with app.app_context():
        admin = Admin.query.filter_by(username='admin').first()
        if admin:
            print(f"Admin user exists with ID: {admin.id}")
            print(f"Username: {admin.username}")
        else:
            print("No admin user found")

if __name__ == '__main__':
    check_admin() 