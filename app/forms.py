from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError

class JobForm(FlaskForm):
    customer_name = StringField('Name', validators=[DataRequired(), Length(min=2, max=120)])
    customer_phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    address = StringField('Address', validators=[DataRequired()])
    service_type = SelectField('Service Type', choices=[
        ('lockout', 'Lockout Service'),
        ('rekey', 'Rekey Service'),
        ('repair', 'Lock Repair'),
        ('install', 'New Installation')
    ])
    submit = SubmitField('Create Job')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(str(i), '⭐' * i) for i in range(1, 6)], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Length(max=500)])
    submit = SubmitField('Submit Review')

class LocksmithProfileForm(FlaskForm):
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=120)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=20)])
    email = StringField('Email', validators=[Email(), Length(max=120)])
    service_area = StringField('Service Area', validators=[DataRequired()])
    submit = SubmitField('Update Profile')
