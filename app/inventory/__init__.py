from flask_smorest import Blueprint

inventory_bp = Blueprint("inventory",__name__ , url_prefix="/api/v1/inventory", description="Operations related to inventory management and logs")

from . import routes