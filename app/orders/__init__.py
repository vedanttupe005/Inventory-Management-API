from flask import Blueprint

orders_bp = Blueprint("oreders",__name__,url_prefix="api/v1/orders")

from . import routes