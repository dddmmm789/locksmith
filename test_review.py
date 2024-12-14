from app import create_app, db
from app.models.locksmith import Locksmith
from app.models.job import Job
from datetime import datetime
import os
import shutil

def setup_test():
    app = create_app()
    
    with app.app_context():
        # Create uploads directory if it doesn't exist
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Create images directory if it doesn't exist
        images_dir = os.path.join(app.root_path, 'static', 'images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Handle default profile image
        default_image = os.path.join(images_dir, 'default_profile.jpg')
        if not os.path.exists(default_image):
            try:
                # Try to create an image using Pillow
                from PIL import Image
                img = Image.new('RGB', (200, 200), color='blue')
                img.save(default_image)
                print(f"Created default profile image at {default_image}")
            except ImportError:
                # If Pillow is not available, copy from a template if it exists
                template_image = os.path.join(app.root_path, 'static', 'images', 'template_profile.jpg')
                if os.path.exists(template_image):
                    shutil.copy2(template_image, default_image)
                    print(f"Copied template profile image to {default_image}")
                else:
                    print("Warning: No default profile image available")
        
        # Create test locksmith
        locksmith = Locksmith.query.filter_by(phone_number='+11234567890').first()
        if not locksmith:
            locksmith = Locksmith(
                name='Test Locksmith',
                phone_number='+11234567890',
                email='test@example.com',
                status='approved',
                profile_photo='default_profile.jpg',
                phone_verified=True
            )
            db.session.add(locksmith)
            db.session.commit()
            print(f"Created test locksmith with ID: {locksmith.id}")
        else:
            print(f"Using existing locksmith with ID: {locksmith.id}")
            # Ensure locksmith is approved
            if locksmith.status != 'approved':
                locksmith.status = 'approved'
                locksmith.phone_verified = True
                db.session.commit()
                print("Updated locksmith status to approved")
        
        # Create test job
        job = Job(
            customer_phone='+10987654321',
            customer_address='123 Test St, New York, NY',
            locksmith_id=locksmith.id,
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(job)
        db.session.commit()
        print(f"Created test job with tracking ID: {job.tracking_id}")
        
        # Print test URLs
        base_url = 'http://127.0.0.1:5001'
        print("\nTest URLs:")
        print(f"1. Review Form: {base_url}/locksmith/job/{job.tracking_id}/review")
        print(f"2. Reviews Page: {base_url}/locksmith/reviews/{locksmith.id}")
        print(f"3. Tracking Page: {base_url}/track/{job.tracking_id}")
        
        return {
            'locksmith_id': locksmith.id,
            'tracking_id': job.tracking_id,
            'urls': {
                'review_form': f"{base_url}/locksmith/job/{job.tracking_id}/review",
                'reviews_page': f"{base_url}/locksmith/reviews/{locksmith.id}",
                'tracking_page': f"{base_url}/track/{job.tracking_id}"
            }
        }

if __name__ == '__main__':
    print("Setting up test environment...")
    result = setup_test()
    print("\nSetup complete!")
    print("\nTest URLs:")
    print(f"1. Review Form: {result['urls']['review_form']}")
    print(f"2. Reviews Page: {result['urls']['reviews_page']}")
    print(f"3. Tracking Page: {result['urls']['tracking_page']}")
    print("\nIDs for reference:")
    print(f"Locksmith ID: {result['locksmith_id']}")
    print(f"Tracking ID: {result['tracking_id']}") 