from app.inventory import inventory_bp
from flask import Blueprint, request, jsonify
from app import model
from app.extensions import db,cache
from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required

from app.schema.inventory_log_schema import  InventoryLogResponseSchema

@inventory_bp.route("/logs", methods=["GET"])
@jwt_required()
@role_required("admin", "staff", "manager","user")
def get_inventory_logs():
    product_id = request.args.get("product_id",type=int)
    if product_id :
        product_log = db.session.query(model.InventoryLog).filter_by(product_id=product_id).order_by(model.InventoryLog.timestamp.desc())

        if not product_log:
            return jsonify({"message": "No inventory logs found for the specified product_id."}), 404

    else:
        product_log = db.session.query(model.InventoryLog).order_by(model.InventoryLog.timestamp.desc())

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    pagination = product_log.paginate(page=page, per_page=limit, error_out=False)

    log = InventoryLogResponseSchema(many=True).dump(pagination.items)

    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "items": log
    }, 200

@inventory_bp.route("/logs/low-stock", methods=["GET"])
@jwt_required()
@role_required("admin", "staff", "manager","user")
@cache.cached(timeout=300, query_string=True)
def get_low_stock_logs():
    threshold = request.args.get("threshold", default=10, type=int)

    low_stock_logs = db.session.query(model.InventoryLog).join(model.Product).filter(model.Product.quantity < threshold).order_by(model.InventoryLog.timestamp.desc())

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)

    pagination = low_stock_logs.paginate(page=page, per_page=limit, error_out=False)

    log = InventoryLogResponseSchema(many=True).dump(pagination.items)

    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "items": log
    }, 200