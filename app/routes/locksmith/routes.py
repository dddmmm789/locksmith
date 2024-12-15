from flask import render_template, redirect, url_for, request, flash
from app.routes.locksmith import bp

@bp.route('/dashboard')
def dashboard():
    return render_template('locksmith/dashboard.html', active_jobs=[])

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle login logic here
        return redirect(url_for('locksmith.dashboard'))
    return render_template('locksmith/login.html')

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Handle signup logic here
        return redirect(url_for('locksmith.complete_profile'))
    return render_template('locksmith/signup.html')
