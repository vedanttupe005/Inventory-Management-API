from flask_smorest import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth', description='Authentication and user management operations')

from . import routes