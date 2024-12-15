import random
import string
from twilio.rest import Client
from flask import current_app
import googlemaps

def generate_tracking_id():
    """Generate a unique tracking ID for jobs"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=8))

def send_sms(phone_number, message):
    """Send SMS using Twilio"""
    client = Client(
        current_app.config['TWILIO_ACCOUNT_SID'],
        current_app.config['TWILIO_AUTH_TOKEN']
    )
    
    try:
        message = client.messages.create(
            body=message,
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=phone_number
        )
        return True, message.sid
    except Exception as e:
        return False, str(e)

def geocode_address(address):
    """Convert address to coordinates using Google Maps"""
    gmaps = googlemaps.Client(key=current_app.config['GOOGLE_MAPS_API_KEY'])
    
    try:
        result = gmaps.geocode(address)
        if result:
            location = result[0]['geometry']['location']
            return True, (location['lat'], location['lng'])
        return False, "Address not found"
    except Exception as e:
        return False, str(e)
