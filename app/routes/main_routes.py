from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/terms')
def terms():
    terms_content = """
    <h1>Terms and Conditions</h1>
    <p>Effective Date: 12.15.2024</p>
    <p>Welcome to Locksmith MVP (the "Service"). These Terms and Conditions ("Terms") and Privacy Policy govern your use of this Service, developed and provided by the owners of this domain ("we," "us," or "our").</p>
    
    <h2>1. Free Use with Future Changes</h2>
    <p>The Service is currently free of charge.</p>
    <p>We reserve the right to modify, limit, charge fees, or restrict access to the Service at any time, without prior notice.</p>
    
    <!-- Add full terms content here -->
    """
    return render_template('legal/terms.html', terms_content=terms_content)

@bp.route('/')
def index():
    return render_template('index.html')
