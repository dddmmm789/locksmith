from app.extensions import db
from datetime import datetime
from flask import url_for

class Locksmith(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    profile_photo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone_verified = db.Column(db.Boolean, default=False)
    otp_code = db.Column(db.String(6))
    otp_expires_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    application_date = db.Column(db.DateTime)
    application_notes = db.Column(db.Text)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('admin.id'))
    jobs = db.relationship('Job', backref='locksmith', lazy=True)
    tagline = db.Column(db.String(100))
    years_experience = db.Column(db.Integer)
    license_number = db.Column(db.String(50))
    service_areas = db.Column(db.String(500))

    @property
    def profile_photo_url(self):
        if self.profile_photo:
            return url_for('static', filename=f'uploads/{self.profile_photo}')
        return url_for('static', filename='images/default_profile.jpg')