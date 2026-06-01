from flask import Blueprint

category_bp = Blueprint("categories", __name__, url_prefix="/api/v1/categories")

from . import routes