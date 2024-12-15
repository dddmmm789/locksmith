from flask import Blueprint

bp = Blueprint('locksmith', __name__, url_prefix='/locksmith')

from app.routes.locksmith import routes
