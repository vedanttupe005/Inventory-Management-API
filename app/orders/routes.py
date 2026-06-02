from flask import Blueprint

orders_bp = Blueprint("oreders",__name__,url_prefix="/orders")

from . import routes

