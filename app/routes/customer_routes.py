from flask import Blueprint, render_template, jsonify, request, current_app, make_response
from app.extensions import db
from app.models.job import Job
from app.models.review import Review
import googlemaps
from datetime import datetime, timedelta

bp = Blueprint('customer', __name__, url_prefix='/track')

@bp.route('/<tracking_id>')
def tracking(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    
    # Update view count
    job.view_count = (job.view_count or 0) + 1
    job.last_viewed = datetime.utcnow()
    
    # Calculate average rating
    reviews = Review.query.filter_by(locksmith_id=job.locksmith_id).all()
    avg_rating = 0
    total_reviews = len(reviews)
    if total_reviews > 0:
        avg_rating = round(sum(r.rating for r in reviews) / total_reviews, 1)
    
    # Get initial location data
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    dest_result = gmaps.geocode(job.customer_address)
    
    initial_data = {
        'eta': '15 mins',
        'distance': '8.5 mi',
        'duration': '22 mins'
    }
    
    if dest_result:
        initial_data['destination'] = {
            'lat': dest_result[0]['geometry']['location']['lat'],
            'lng': dest_result[0]['geometry']['location']['lng']
        }
    
    response = make_response(render_template(
        'customer/tracking.html',
        job=job,
        avg_rating=avg_rating,
        total_reviews=total_reviews,
        initial_data=initial_data,
        GOOGLE_MAPS_API_KEY=current_app.config.get('GOOGLE_MAPS_API_KEY')
    ))
    
    db.session.commit()
    return response

@bp.route('/api/location/<tracking_id>')
def get_location(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    
    # Default starting location (Bergenfield office)
    default_address = "28 mallard court, Bergenfield, NJ 07631"
    
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    
    # Get locksmith location coordinates
    start_result = gmaps.geocode(default_address)
    if not start_result:
        return jsonify({'success': False, 'error': 'Invalid start address'})
    
    locksmith_location = {
        'lat': start_result[0]['geometry']['location']['lat'],
        'lng': start_result[0]['geometry']['location']['lng']
    }
    
    # Get destination coordinates
    dest_result = gmaps.geocode(job.customer_address)
    if not dest_result:
        return jsonify({'success': False, 'error': 'Invalid destination address'})
    
    destination = {
        'lat': dest_result[0]['geometry']['location']['lat'],
        'lng': dest_result[0]['geometry']['location']['lng']
    }
    
    # Get route details
    directions = gmaps.directions(
        default_address,
        job.customer_address,
        mode="driving"
    )
    
    if directions:
        route = directions[0]['legs'][0]
        eta = (datetime.now() + timedelta(minutes=15)).strftime('%I:%M %p')
        
        return jsonify({
            'success': True,
            'locksmith_location': locksmith_location,
            'destination_lat': destination['lat'],
            'destination_lng': destination['lng'],
            'route': directions[0]['overview_polyline']['points'],  # Add route polyline
            'eta': eta,
            'distance': route['distance']['text'],
            'duration': route['duration']['text'],
            'job_completed': job.status == 'completed'
        })
    
    return jsonify({'success': False, 'error': 'Could not calculate route'})

@bp.route('/api/update-address', methods=['POST'])
def update_address():
    try:
        data = request.get_json()
        print("Received address update data:", data)
        
        if not data or 'tracking_id' not in data or 'address' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing tracking_id or address'
            }), 400
            
        job = Job.query.filter_by(tracking_id=data['tracking_id']).first_or_404()
        
        # Validate the address using Google Geocoding API
        gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
        geocode_result = gmaps.geocode(data['address'])
        
        if not geocode_result:
            return jsonify({
                'success': False,
                'error': 'Invalid address. Please enter a valid address.'
            }), 400
        
        # Get formatted address from Google but preserve location details
        formatted_address = geocode_result[0]['formatted_address']
        current_details = job.location_details  # Store current details
        job.customer_address = formatted_address
        job.location_details = current_details  # Preserve details
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Address updated successfully',
            'formatted_address': formatted_address,
            'location_details': job.location_details
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error updating address: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/update-details', methods=['POST'])
def update_details():
    try:
        data = request.get_json()
        job = Job.query.filter_by(tracking_id=data['tracking_id']).first_or_404()
        job.location_details = data['details']
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/api/confirm-address', methods=['POST'])
def confirm_address():
    try:
        data = request.get_json()
        job = Job.query.filter_by(tracking_id=data['tracking_id']).first_or_404()
        job.address_confirmed = True
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Address confirmed'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500