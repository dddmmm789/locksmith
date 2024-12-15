import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db
from app.models.admin import Admin

def create_admin_user(username='admin', password='admin123'):  # You can change the default password
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
    create_admin_user() 