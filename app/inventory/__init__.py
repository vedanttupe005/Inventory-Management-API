from flask import Blueprint

inventory_bp = Blueprint("inventory",__name__ , url_prefix="api/v1/inventory")

from . import routes