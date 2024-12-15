from flask import Blueprint, jsonify, request
from app.models import Job, Locksmith
from app.utils import geocode_address, send_sms
from app import db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/job/<tracking_id>/location')
def job_location(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    return jsonify({
        'latitude': job.latitude,
        'longitude': job.longitude,
        'status': job.status,
        'locksmith_eta': job.eta
    })

@bp.route('/job/<tracking_id>/update-status', methods=['POST'])
def update_job_status(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    data = request.get_json()
    
    job.status = data['status']
    if 'location' in data:
        job.latitude = data['location']['lat']
        job.longitude = data['location']['lng']
    
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/locksmith/availability', methods=['POST'])
def update_availability():
    data = request.get_json()
    locksmith = Locksmith.query.get_or_404(data['locksmith_id'])
    locksmith.is_available = data['available']
    db.session.commit()
    return jsonify({'success': True})
