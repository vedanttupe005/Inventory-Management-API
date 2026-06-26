from flask_smorest import Blueprint

products_bp = Blueprint("products", __name__, url_prefix="/api/v1/products",description="Operations related to products management")

from . import routes