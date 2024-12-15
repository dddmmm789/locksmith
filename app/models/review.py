from app import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    locksmith_id = db.Column(db.Integer, db.ForeignKey('locksmith.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    reviewer_name = db.Column(db.String(100))
    review_date = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=True)
    job_type = db.Column(db.String(100))  # e.g., "Lock Change", "Emergency Lockout"
    location = db.Column(db.String(100))  # City, State 