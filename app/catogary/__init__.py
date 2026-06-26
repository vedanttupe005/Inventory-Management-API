from flask_smorest import Blueprint

category_bp = Blueprint("Categories", __name__, url_prefix="/api/v1/categories",description="Operations related to product categories")

from . import routes