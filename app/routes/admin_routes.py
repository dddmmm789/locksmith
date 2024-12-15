from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session
from app.extensions import db
from app.models.locksmith import Locksmith
from app.scripts.populate_reviews import create_sample_reviews
from app.models.review import Review
from app.models.admin import Admin
from functools import wraps
from datetime import datetime
from twilio.rest import Client
from werkzeug.security import generate_password_hash

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in first.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@admin_required
def dashboard():
    print("Accessing admin dashboard")  # Debug print
    locksmiths = Locksmith.query.all()
    print(f"Found {len(locksmiths)} locksmiths")  # Debug print
    return render_template('admin/dashboard.html', locksmiths=locksmiths)

@bp.route('/generate-reviews/<int:locksmith_id>', methods=['POST'])
def generate_reviews(locksmith_id):
    try:
        create_sample_reviews(locksmith_id, num_reviews=10)  # Generate 10 reviews
        return jsonify({
            'success': True,
            'message': 'Reviews generated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@bp.route('/reviews/<int:review_id>/delete', methods=['POST'])
def delete_review(review_id):
    try:
        review = Review.query.get_or_404(review_id)
        db.session.delete(review)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Review deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt - Username: {username}")
        
        admin = Admin.query.filter_by(username=username).first()
        if admin:
            print(f"Found admin user (ID: {admin.id})")
            print(f"Stored hash: {admin.password_hash}")
            
            # Generate hash for the provided password
            test_hash = generate_password_hash(password)
            print(f"Test hash: {test_hash}")
            
            if admin.check_password(password):
                print("Password verified")
                session.clear()
                session['admin_id'] = admin.id
                session.permanent = True
                print(f"Session set: {session.get('admin_id')}")
                return redirect(url_for('admin.dashboard'))
            else:
                print("Invalid password")
        else:
            print("Admin user not found")
        
        flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

@bp.route('/locksmith/<int:locksmith_id>/delete', methods=['POST'])
@admin_required
def delete_locksmith(locksmith_id):
    locksmith = Locksmith.query.get_or_404(locksmith_id)
    db.session.delete(locksmith)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/applications')
@admin_required
def applications():
    print("Accessing applications page")  # Debug print
    pending = Locksmith.query.filter_by(status='pending').order_by(Locksmith.application_date.desc()).all()
    print(f"Found {len(pending)} pending applications")  # Debug print
    return render_template('admin/applications.html', applications=pending)

@bp.route('/application/<int:locksmith_id>/review', methods=['POST'])
@admin_required
def review_application(locksmith_id):
    locksmith = Locksmith.query.get_or_404(locksmith_id)
    action = request.form.get('action')
    notes = request.form.get('notes')
    
    if action not in ['approve', 'reject']:
        return jsonify({'success': False, 'error': 'Invalid action'})
    
    locksmith.status = 'approved' if action == 'approve' else 'rejected'
    locksmith.application_notes = notes
    locksmith.reviewed_at = datetime.utcnow()
    locksmith.reviewed_by = session['admin_id']
    
    db.session.commit()
    
    # Send notification to locksmith
    try:
        client = Client(current_app.config['TWILIO_ACCOUNT_SID'],
                       current_app.config['TWILIO_AUTH_TOKEN'])
        
        message = (
            f"Your application to join our locksmith network has been {'approved' if action == 'approve' else 'rejected'}. "
            f"{'You can now log in and start accepting jobs.' if action == 'approve' else notes}"
        )
        
        client.messages.create(
            body=message,
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=locksmith.phone_number
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")
    
    return jsonify({'success': True})