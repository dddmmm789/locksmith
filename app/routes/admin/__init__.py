from flask import Blueprint

bp = Blueprint('admin', __name__, url_prefix='/admin')

from app.routes.admin import routes