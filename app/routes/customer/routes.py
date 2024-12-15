from flask import render_template
from app.routes.customer import bp

@bp.route('/<tracking_id>')
def tracking(tracking_id):
    return render_template('customer/tracking.html')
