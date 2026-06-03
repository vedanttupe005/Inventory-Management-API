from app.orders import orders_bp
from app.schema.order_schema import OrderCreateSchema, OrderResponseSchema
from marshmallow import ValidationError
from app.model import Order, OrderItems, Product, InventoryLog
from app.extensions import db
from flask import request

from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils.decorators import role_required


@orders_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin", "user", "staff", "manager")
def create_order():
    try:
        data = OrderCreateSchema().load(request.get_json())
    except ValidationError as err:
        return {"error": err.messages}, 400

    try:
        total_amount = 0
        validated_items = []
        seen_products = set()

        # Validation Phase
        for item in data["items"]:

            if item["product_id"] in seen_products:
                return {
                    "error": f"Duplicate product_id {item['product_id']} in order"
                }, 400

            seen_products.add(item["product_id"])

            product = Product.query.get(item["product_id"])

            if not product:
                return {
                    "error": f"Product with id {item['product_id']} not found"
                }, 404

            if product.quantity < item["quantity"]:
                return {
                    "error": f"Not enough stock for product {product.name}"
                }, 400

            total_amount += product.price * item["quantity"]

            validated_items.append({
                "product": product,
                "quantity": item["quantity"]
            })

        # Create Order
        order = Order(
            user_id=get_jwt_identity(),
            total_amount=total_amount
        )

        db.session.add(order)
        db.session.flush()# to get the order ID before committing

        # Create Order Items & Update Inventory
        for item in validated_items:

            product = item["product"]

            order_item = OrderItems(
                order_id=order.id,
                product_id=product.id,
                quantity=item["quantity"],
                price=product.price
            )

            db.session.add(order_item)

            product.quantity -= item["quantity"]

            inventory_log = InventoryLog(
                user_id=get_jwt_identity(),
                product_id=product.id,
                change_type="order",
                quantity_changed=-item["quantity"]
            )

            db.session.add(inventory_log)

        db.session.commit()

        return {
            "message": "Order created successfully",
            "order_id": order.id,
            "status": order.status,
            "total_amount": float(order.total_amount)
        }, 201

    except Exception as e:
        db.session.rollback()

        return {
            "error": "Failed to create order",
            "details": str(e)
        }, 500



@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
@role_required("admin", "manager", "staff", "user")
def get_order(order_id):

    order = db.session.get(Order, order_id)

    if not order:
        return {"error": "Order not found"}, 404

    role = get_jwt()["role"]

    if role not in ["admin", "manager"]:
        if order.user_id != get_jwt_identity():
            return {"error": "Access denied"}, 403

    return OrderResponseSchema().dump(order), 200





@orders_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin", "manager", "staff", "user")
def get_orders():

    role = get_jwt()["role"]

    query = Order.query

    if role not in ["admin", "manager"]:
        query = query.filter_by(
            user_id=get_jwt_identity()
        )

    orders = query.order_by(
        Order.created_at.desc()
    ).all()

    return {
        "orders": OrderResponseSchema(many=True).dump(orders)
    }, 200