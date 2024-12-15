from flask import Blueprint

bp = Blueprint('customer', __name__, url_prefix='/track')

from app.routes.customer import routes
