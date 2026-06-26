from flask_smorest import Blueprint

orders_bp = Blueprint("oreders",__name__,url_prefix="/api/v1/orders",description="Operations related to orders management")

from . import routes