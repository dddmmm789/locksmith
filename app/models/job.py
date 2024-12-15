from app.extensions import db
from datetime import datetime
import uuid

class Job(db.Model):
    """Job model representing a locksmith service request."""
    id = db.Column(db.Integer, primary_key=True)
    tracking_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    locksmith_id = db.Column(db.Integer, db.ForeignKey('locksmith.id'), nullable=False)
    last_viewed = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)
    location_details = db.Column(db.Text, nullable=True)
    address_confirmed = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Job {self.tracking_id}>'