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
    
    # Update view statistics
    now = datetime.utcnow()
    job.last_viewed = now
    job.view_count = (job.view_count or 0) + 1
    db.session.commit()
    
    # Add timestamp to response headers to prevent caching
    response = make_response(render_template(
        'customer/tracking.html',
        job=job,
        total_reviews=Review.query.filter_by(locksmith_id=job.locksmith.id).count()
    ))
    response.headers['Last-Modified'] = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response

@bp.route('/api/location/<tracking_id>')
def get_location(tracking_id):
    job = Job.query.filter_by(tracking_id=tracking_id).first_or_404()
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    
    try:
        # Default dispatch location
        dispatch_address = "28 mallard court, Bergenfield, NJ 07631"
        dispatch_result = gmaps.geocode(dispatch_address)
        
        if dispatch_result:
            locksmith_location = {
                'lat': dispatch_result[0]['geometry']['location']['lat'],
                'lng': dispatch_result[0]['geometry']['location']['lng']
            }
            
            # Get route to destination
            directions = gmaps.directions(
                dispatch_address,
                job.customer_address,
                mode='driving'
            )
            
            if directions:
                route = directions[0]
                duration = route['legs'][0]['duration']['text']
                distance = route['legs'][0]['distance']['text']
                
                # Calculate arrival time
                arrival_time = (datetime.now() + 
                              timedelta(minutes=int(route['legs'][0]['duration']['value']/60))
                             ).strftime('%I:%M %p')
                
                return jsonify({
                    'success': True,
                    'job_completed': job.status == 'completed',
                    'locksmith_location': locksmith_location,
                    'eta': f"Arriving at {arrival_time}",
                    'duration': duration,
                    'distance': distance,
                    'route': route['overview_polyline']['points']
                })
        
        return jsonify({
            'success': False,
            'error': 'Could not calculate route'
        })
            
    except Exception as e:
        print(f"Error in get_location: {str(e)}")  # Debug print
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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