from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify, session
from app.extensions import db
from app.models.locksmith import Locksmith
from app.models.job import Job
from app.models.review import Review
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from twilio.rest import Client
import json
import random

bp = Blueprint('locksmith', __name__, url_prefix='/locksmith')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

def format_phone_number(phone):
    """Format phone number to E.164 format"""
    # Remove any non-digit characters
    phone = ''.join(filter(str.isdigit, phone))
    
    # Add country code if not present
    if len(phone) == 10:
        phone = '1' + phone
    elif len(phone) > 10 and not phone.startswith('1'):
        phone = '1' + phone
    
    # Add plus sign
    phone = '+' + phone
    
    return phone

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        name = request.form.get('name')
        phone_number = request.form.get('phone_number')
        photo = request.files.get('profile_photo')
        
        if not all([name, phone_number]):
            flash('Name and phone number are required', 'error')
            return redirect(url_for('locksmith.profile'))
        
        locksmith = Locksmith(name=name, phone_number=phone_number)
        
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            locksmith.profile_photo = filename
        
        db.session.add(locksmith)
        db.session.commit()
        
        flash('Profile created successfully!', 'success')
        return redirect(url_for('locksmith.dashboard'))
    
    return render_template('locksmith/profile.html')

@bp.route('/job/new', methods=['GET', 'POST'])
def new_job():
    # First check if logged in
    locksmith_id = session.get('locksmith_id')
    if not locksmith_id:
        flash('Please log in first', 'error')
        return redirect(url_for('locksmith.login'))

    if request.method == 'POST':
        # Get form data
        customer_phone = request.form.get('customer_phone')
        customer_address = request.form.get('customer_address')
        
        print(f"DEBUG - Creating job:")
        print(f"Locksmith ID: {locksmith_id}")
        print(f"Customer Phone: {customer_phone}")
        print(f"Customer Address: {customer_address}")
        
        if not all([customer_phone, customer_address]):
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('locksmith.new_job'))
        
        try:
            # Create new job
            job = Job(
                customer_phone=customer_phone,
                customer_address=customer_address,
                locksmith_id=locksmith_id,
                status='active',
                created_at=datetime.utcnow()
            )
            
            db.session.add(job)
            db.session.commit()
            
            print(f"DEBUG - Job created successfully:")
            print(f"Job ID: {job.id}")
            print(f"Tracking ID: {job.tracking_id}")
            
            flash('Job created successfully!', 'success')
            return redirect(url_for('locksmith.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG - Error creating job: {str(e)}")
            flash(f'Error creating job: {str(e)}', 'error')
            return redirect(url_for('locksmith.new_job'))
    
    # GET request - show form
    return render_template('locksmith/job_form.html')

@bp.route('/dashboard')
def dashboard():
    locksmith_id = session.get('locksmith_id')
    if not locksmith_id:
        flash('Please log in first', 'error')
        return redirect(url_for('locksmith.login'))
    
    locksmith = Locksmith.query.get_or_404(locksmith_id)
    
    # Get jobs
    active_jobs = Job.query.filter_by(
        locksmith_id=locksmith_id,
        status='active'
    ).order_by(Job.created_at.desc()).all()
    
    completed_jobs = Job.query.filter_by(
        locksmith_id=locksmith_id,
        status='completed'
    ).order_by(Job.completed_at.desc()).all()
    
    # Get reviews
    recent_reviews = Review.query.filter_by(locksmith_id=locksmith_id)\
        .order_by(Review.review_date.desc())\
        .limit(3)\
        .all()
    total_reviews = Review.query.filter_by(locksmith_id=locksmith_id).count()
    
    return render_template('locksmith/dashboard.html',
                         locksmith=locksmith,
                         active_jobs=active_jobs,
                         completed_jobs=completed_jobs,
                         recent_reviews=recent_reviews,
                         total_reviews=total_reviews)

@bp.route('/job/<tracking_id>/send-link', methods=['POST'])
def send_tracking_link(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    
    try:
        # Generate tracking URL
        tracking_url = url_for('customer.tracking', tracking_id=tracking_id, _external=True)
        
        # Initialize Twilio client
        client = Client(current_app.config['TWILIO_ACCOUNT_SID'],
                       current_app.config['TWILIO_AUTH_TOKEN'])
        
        # Send SMS
        message = client.messages.create(
            body=f'Track your locksmith here: {tracking_url}',
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=job.customer_phone
        )
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/job/<tracking_id>/complete', methods=['POST'])
def complete_job(tracking_id):
    try:
        job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
        job.status = 'completed'
        job.completed_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/reviews/<int:locksmith_id>')
def reviews(locksmith_id):
    is_admin = request.args.get('admin', '0') == '1'
    tracking_id = request.args.get('tracking_id')
    
    # Check if it's the locksmith viewing their own reviews
    is_owner = 'locksmith_id' in session and session['locksmith_id'] == locksmith_id
    
    locksmith = Locksmith.query.get_or_404(locksmith_id)
    job = None
    if tracking_id:
        job = Job.query.filter_by(tracking_id=tracking_id).first()
    
    reviews = Review.query.filter_by(locksmith_id=locksmith_id)\
        .order_by(Review.review_date.desc())\
        .all()
    
    # Calculate stats
    total_reviews = len(reviews)
    if total_reviews > 0:
        avg_rating = sum(r.rating for r in reviews) / total_reviews
        rating_counts = {i: len([r for r in reviews if r.rating == i]) for i in range(1, 6)}
    else:
        avg_rating = 0
        rating_counts = {i: 0 for i in range(1, 6)}
    
    return render_template('locksmith/reviews.html',
                         locksmith=locksmith,
                         reviews=reviews,
                         total_reviews=total_reviews,
                         avg_rating=avg_rating,
                         rating_counts=rating_counts,
                         is_admin=is_admin,
                         is_owner=is_owner,  # Pass this to template
                         job=job)

@bp.route('/reviews/<int:locksmith_id>/submit', methods=['POST'])
def submit_review(locksmith_id):
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'rating' not in data:
            return jsonify({
                'success': False,
                'error': 'Rating is required'
            }), 400
            
        # Create review
        review = Review(
            locksmith_id=locksmith_id,
            rating=int(data['rating']),
            comment=data.get('comment', '').strip() or None,
            reviewer_name=data.get('reviewer_name', '').strip() or None,
            verified=True,
            review_date=datetime.utcnow()
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Review submitted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting review: {str(e)}")  # Add debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/job/<tracking_id>/reverse-completion', methods=['POST'])
def reverse_job_completion(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    
    try:
        # Toggle completion status
        if job.status == 'completed':
            job.status = 'active'
            job.completed_at = None
            message = 'Job status reversed to active'
        else:
            job.status = 'completed'
            job.completed_at = datetime.utcnow()
            message = 'Job marked as completed'
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'new_status': job.status
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            phone_number = request.form.get('phone_number')
            
            # Format phone number
            phone_number = format_phone_number(phone_number)
            
            # Get existing locksmith by phone number
            locksmith = Locksmith.query.filter_by(phone_number=phone_number).first()
            
            if not locksmith or not locksmith.phone_verified:
                flash('Please complete phone verification first', 'error')
                return redirect(url_for('locksmith.signup'))
            
            # Update existing locksmith with form data
            locksmith.name = name
            locksmith.email = email if email else None  # Set to None if empty
            locksmith.status = 'pending'
            locksmith.application_date = datetime.utcnow()
            
            # Handle profile photo
            photo = request.files.get('profile_photo')
            if photo and allowed_file(photo.filename):
                filename = secure_filename(photo.filename)
                # Create upload directory if it doesn't exist
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)
                locksmith.profile_photo = filename
            
            db.session.commit()
            
            # Store locksmith ID in session
            session['locksmith_id'] = locksmith.id
            session.modified = True
            
            # Redirect to application status
            return redirect(url_for('locksmith.application_status', id=locksmith.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error during signup. Please try again.', 'error')
            return redirect(url_for('locksmith.signup'))
    
    return render_template('locksmith/signup.html', locksmith=None)

@bp.route('/signup/send-otp', methods=['POST'])
def send_otp():
    try:
        phone = request.form.get('phone_number')
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number required'})
        
        phone = format_phone_number(phone)
        otp = generate_otp()
        expires = datetime.utcnow() + timedelta(minutes=10)
        
        locksmith = Locksmith.query.filter_by(phone_number=phone).first()
        if not locksmith:
            locksmith = Locksmith(phone_number=phone)
            db.session.add(locksmith)
        
        locksmith.otp_code = otp
        locksmith.otp_expires_at = expires
        db.session.commit()
        
        return jsonify({'success': True})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to send verification code'})

@bp.route('/signup/verify-otp', methods=['POST'])
def verify_otp():
    try:
        phone = format_phone_number(request.form.get('phone_number'))
        otp = request.form.get('otp')
        
        # Debug mode: Auto-verify with code "123456"
        if current_app.debug and otp == "123456":
            locksmith = Locksmith.query.filter_by(phone_number=phone).first()
            if not locksmith:
                locksmith = Locksmith(phone_number=phone)
                db.session.add(locksmith)
            locksmith.phone_verified = True
            db.session.commit()
            return jsonify({'success': True})
        
        # Production verification
        locksmith = Locksmith.query.filter_by(phone_number=phone).first()
        if not locksmith:
            return jsonify({'success': False, 'error': 'Invalid phone number'})
        
        if locksmith.otp_code != otp:
            return jsonify({'success': False, 'error': 'Invalid verification code'})
        
        if datetime.utcnow() > locksmith.otp_expires_at:
            return jsonify({'success': False, 'error': 'Verification code expired'})
        
        locksmith.phone_verified = True
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Verification failed'})

@bp.route('/application-status/<int:id>')
def application_status(id):
    print(f"Accessing application status for ID: {id}")  # Debug print
    
    # Verify this is the correct locksmith
    if 'locksmith_id' not in session:
        print("No locksmith_id in session")  # Debug print
        flash('Please complete signup first', 'error')
        return redirect(url_for('locksmith.signup'))
        
    if session['locksmith_id'] != id:
        print(f"Session ID ({session['locksmith_id']}) doesn't match URL ID ({id})")  # Debug print
        flash('Invalid access', 'error')
        return redirect(url_for('locksmith.signup'))
    
    locksmith = Locksmith.query.get_or_404(id)
    print(f"Found locksmith: {locksmith.name}, Status: {locksmith.status}")  # Debug print
    
    return render_template('locksmith/application_status.html', locksmith=locksmith)

@bp.route('/debug/routes')
def debug_routes():
    """List all registered routes"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint.startswith('locksmith.'):
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'url': str(rule)
            })
    return jsonify(routes)

@bp.route('/debug')
def debug():
    return jsonify({
        'message': 'Locksmith blueprint is working',
        'routes': [str(rule) for rule in current_app.url_map.iter_rules()]
    })

@bp.route('/update-profile/<int:id>', methods=['POST'])
def update_profile(id):
    if 'locksmith_id' not in session or session['locksmith_id'] != id:
        flash('Please log in to update your profile', 'error')
        return redirect(url_for('locksmith.login'))
    
    locksmith = Locksmith.query.get_or_404(id)
    
    try:
        # Update profile fields
        locksmith.tagline = request.form.get('tagline')
        locksmith.years_experience = request.form.get('experience')
        locksmith.license_number = request.form.get('license')
        locksmith.service_areas = ','.join(request.form.getlist('areas[]'))
        
        # Handle profile photo
        photo = request.files.get('profile_photo')
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            locksmith.profile_photo = filename
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        
        # Redirect to dashboard instead of application status
        return redirect(url_for('locksmith.dashboard'))
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating profile', 'error')
        return redirect(url_for('locksmith.dashboard'))

@bp.route('/login', methods=['GET'])
def login():
    if 'locksmith_id' in session:
        return redirect(url_for('locksmith.dashboard'))
    return render_template('locksmith/login.html')

@bp.route('/edit-profile/<int:id>', methods=['GET'])
def edit_profile(id):
    if 'locksmith_id' not in session or session['locksmith_id'] != id:
        flash('Please log in to edit your profile', 'error')
        return redirect(url_for('locksmith.login'))
    
    locksmith = Locksmith.query.get_or_404(id)
    return render_template('locksmith/edit_profile.html', locksmith=locksmith)

@bp.route('/job/<tracking_id>/review', methods=['GET', 'POST'])
def job_review(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            review = Review(
                locksmith_id=job.locksmith_id,
                rating=int(data['rating']),
                comment=data.get('comment', '').strip() or None,
                reviewer_name=data.get('reviewer_name', '').strip() or None,
                verified=True,
                review_date=datetime.utcnow()
            )
            
            db.session.add(review)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Review submitted successfully'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return render_template('locksmith/job_review.html', job=job)

@bp.route('/debug/review/<tracking_id>')
def debug_review(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    return jsonify({
        'job': {
            'id': job.id,
            'tracking_id': job.tracking_id,
            'status': job.status,
            'locksmith_id': job.locksmith_id
        },
        'locksmith': {
            'id': job.locksmith.id,
            'name': job.locksmith.name
        },
        'reviews': [{
            'rating': r.rating,
            'comment': r.comment
        } for r in Review.query.filter_by(locksmith_id=job.locksmith_id).all()]
    })

@bp.route('/debug/create-test-job')
def create_test_job():
    try:
        # First, create and approve a test locksmith
        test_phone = '+11234567890'
        locksmith = Locksmith.query.filter_by(phone_number=test_phone).first()
        
        if not locksmith:
            print("Creating new test locksmith...")
            locksmith = Locksmith(
                name='Test Locksmith',
                phone_number=test_phone,
                email='test@example.com',
                status='approved',  # Make sure status is approved
                profile_photo='default.jpg',
                phone_verified=True  # Make sure phone is verified
            )
            db.session.add(locksmith)
            db.session.commit()
            print(f"Created locksmith with ID: {locksmith.id}")
        else:
            print(f"Using existing locksmith with ID: {locksmith.id}")
            # Ensure locksmith is approved
            if locksmith.status != 'approved':
                locksmith.status = 'approved'
                locksmith.phone_verified = True
                db.session.commit()
                print("Updated locksmith status to approved")

        # Create a test job
        print("Creating test job...")
        job = Job(
            customer_phone='+10987654321',
            customer_address='123 Test St, New York, NY',
            locksmith_id=locksmith.id,
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(job)
        db.session.commit()
        print(f"Created job with tracking ID: {job.tracking_id}")

        # Generate test URLs
        review_url = url_for('locksmith.job_review', tracking_id=job.tracking_id, _external=True)
        reviews_page = url_for('locksmith.reviews', locksmith_id=locksmith.id, _external=True)
        debug_url = url_for('locksmith.debug_review', tracking_id=job.tracking_id, _external=True)

        print(f"Review form URL: {review_url}")
        print(f"Reviews page URL: {reviews_page}")

        return jsonify({
            'success': True,
            'message': 'Test job created successfully',
            'test_urls': {
                'review_form': review_url,
                'reviews_page': reviews_page,
                'debug_info': debug_url
            },
            'job': {
                'tracking_id': job.tracking_id,
                'locksmith_id': locksmith.id
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error creating test job: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/debug/test')
def test_review_system():
    try:
        # 1. Create test locksmith if doesn't exist
        test_phone = '+11234567890'
        locksmith = Locksmith.query.filter_by(phone_number=test_phone).first()
        
        if not locksmith:
            # Copy default profile photo to uploads directory
            default_photo = 'default_profile.jpg'  # Change this to your default image name
            src_path = os.path.join(current_app.root_path, 'static', 'images', default_photo)
            dest_path = os.path.join(current_app.root_path, 'static', 'uploads', default_photo)
            
            if os.path.exists(src_path):
                import shutil
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(src_path, dest_path)
            
            locksmith = Locksmith(
                name='Test Locksmith',
                phone_number=test_phone,
                email='test@example.com',
                status='approved',
                profile_photo=default_photo,  # Use the default photo name
                phone_verified=True
            )
            db.session.add(locksmith)
            db.session.commit()
        
        # 2. Create test job
        job = Job(
            customer_phone='+10987654321',
            customer_address='123 Test St, New York, NY',
            locksmith_id=locksmith.id,
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(job)
        db.session.commit()
        
        # 3. Generate all relevant URLs
        urls = {
            'tracking_page': url_for('customer.tracking', tracking_id=job.tracking_id, _external=True),
            'review_form': url_for('locksmith.job_review', tracking_id=job.tracking_id, _external=True),
            'reviews_page': url_for('locksmith.reviews', locksmith_id=locksmith.id, _external=True)
        }
        
        return jsonify({
            'success': True,
            'message': 'Test system created',
            'test_data': {
                'locksmith': {
                    'id': locksmith.id,
                    'name': locksmith.name,
                    'phone': locksmith.phone_number
                },
                'job': {
                    'tracking_id': job.tracking_id,
                    'status': job.status
                }
            },
            'test_urls': urls,
            'instructions': [
                '1. Visit the tracking page to see the job',
                '2. Click the review link to write a review',
                '3. Check the reviews page to see your review'
            ]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/test')
def test():
    return jsonify({
        'message': 'Server is running!',
        'routes': {
            'review_form': url_for('locksmith.job_review', tracking_id='test', _external=True),
            'reviews_page': url_for('locksmith.reviews', locksmith_id=1, _external=True),
            'tracking_page': url_for('customer.tracking', tracking_id='test', _external=True)
        }
    })

@bp.route('/debug/config')
def debug_config():
    return jsonify({
        'debug_mode': current_app.debug,
        'testing': current_app.testing,
        'env': current_app.env
    })

@bp.route('/debug/create-test-locksmith')
def create_test_locksmith():
    try:
        test_phone = '+11234567890'
        locksmith = Locksmith.query.filter_by(phone_number=test_phone).first()
        
        if not locksmith:
            locksmith = Locksmith(
                name='Test Locksmith',
                phone_number=test_phone,
                email='test@example.com',
                status='approved',  # Important: status must be approved to login
                phone_verified=True,
                profile_photo='default_profile.jpg'
            )
            db.session.add(locksmith)
            db.session.commit()
            
        else:
            # Ensure locksmith is approved
            locksmith.status = 'approved'
            locksmith.phone_verified = True
            db.session.commit()
            
        return jsonify({
            'success': True,
            'message': 'Test locksmith created',
            'login_info': {
                'phone': test_phone,
                'otp': '123456',  # Debug OTP code
                'login_url': url_for('locksmith.login', _external=True)
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/login/send-otp', methods=['POST'])
def login_send_otp():
    try:
        phone = request.form.get('phone_number')
        if not phone:
            return jsonify({'success': False, 'error': 'Phone number required'})
        
        phone = format_phone_number(phone)
        
        # Check if locksmith exists and is approved
        locksmith = Locksmith.query.filter_by(phone_number=phone).first()
        if not locksmith:
            return jsonify({'success': False, 'error': 'No account found with this phone number'})
            
        if locksmith.status != 'approved':
            return jsonify({'success': False, 'error': 'Your application is still pending approval'})
        
        # Generate and store OTP
        otp = generate_otp()
        expires = datetime.utcnow() + timedelta(minutes=10)
        
        locksmith.otp_code = otp
        locksmith.otp_expires_at = expires
        db.session.commit()
        
        # In debug mode, print the OTP
        if current_app.debug:
            print(f"Debug - Login OTP for {phone}: {otp}")
        
        return jsonify({'success': True})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to send verification code'})

@bp.route('/login/verify', methods=['POST'])
def login_verify():
    try:
        phone = format_phone_number(request.form.get('phone_number'))
        otp = request.form.get('otp')
        
        locksmith = Locksmith.query.filter_by(phone_number=phone).first()
        if not locksmith:
            return jsonify({'success': False, 'error': 'Invalid phone number'})
            
        # Debug mode: Accept "123456"
        if current_app.debug and otp == "123456":
            session['locksmith_id'] = locksmith.id
            session.modified = True
            return jsonify({
                'success': True,
                'redirect_url': url_for('locksmith.dashboard')
            })
        
        # Production verification
        if locksmith.otp_code != otp:
            return jsonify({'success': False, 'error': 'Invalid verification code'})
        
        if datetime.utcnow() > locksmith.otp_expires_at:
            return jsonify({'success': False, 'error': 'Verification code expired'})
        
        session['locksmith_id'] = locksmith.id
        session.modified = True
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('locksmith.dashboard')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Login failed'})

@bp.route('/debug/check-locksmith/<phone>')
def debug_check_locksmith(phone):
    locksmith = Locksmith.query.filter_by(phone_number=phone).first()
    if not locksmith:
        return jsonify({'exists': False})
    return jsonify({
        'exists': True,
        'id': locksmith.id,
        'status': locksmith.status,
        'phone_verified': locksmith.phone_verified,
        'otp_code': locksmith.otp_code if current_app.debug else None,
        'otp_expires_at': str(locksmith.otp_expires_at) if locksmith.otp_expires_at else None
    })

@bp.route('/debug/test-job')
def test_job_creation():
    locksmith_id = session.get('locksmith_id')
    if not locksmith_id:
        return jsonify({
            'error': 'Not logged in',
            'session_data': dict(session)
        })
    
    try:
        job = Job(
            customer_phone='+11234567890',
            customer_address='Test Address',
            locksmith_id=locksmith_id,
            status='active'
        )
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'job_id': job.id,
            'tracking_id': job.tracking_id,
            'locksmith_id': locksmith_id
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'locksmith_id': locksmith_id
        })