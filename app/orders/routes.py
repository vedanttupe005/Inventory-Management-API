from app.orders import orders_bp
from app.schema.order_schema import OrderCreateSchema, OrderResponseSchema,OrderStatusUpdateSchema
from marshmallow import ValidationError
from app.model import Order, OrderItems, Product, InventoryLog
from app.extensions import db, cache
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

            if item["quantity"] <= 0:
                return {
                    "error": f"Quantity for product {product.name} must be greater than 0"
                }, 400


            product.quantity -= item["quantity"]

            inventory_log = InventoryLog(
                user_id=get_jwt_identity(),
                product_id=product.id,
                change_type="order",
                quantity_changed=-item["quantity"]
            )

            db.session.add(inventory_log)

        db.session.commit()

        cache.clear()  # Clear cache to reflect updated inventory and orders

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

    order = db.session.query(Order).filter_by(id=order_id).first()

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

    query = Order.query # build the base query

    if role not in ["admin", "manager"]:
        query = query.filter_by(
            user_id=get_jwt_identity() # only return orders for the current user if not admin or manager build query don't execute it yet
        )

    query = query.order_by(
        Order.created_at.desc()
    )

    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    if page < 1 or limit < 1:
        return {
            "error": "Page and limit must be positive integers"}, 400
    if limit > 100:
        return {
            "error": "Limit cannot exceed 100"}, 400

    pagination = query.paginate(page=page, per_page=limit, error_out=False) # execute the query with pagination
    paginated_orders = OrderResponseSchema(many=True).dump(pagination.items)

    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "items": paginated_orders
    }, 200




@orders_bp.route("/<int:order_id>/status", methods=["PATCH"])
@jwt_required()
@role_required("admin", "manager")
def update_order_status(order_id):

    try:
        data = OrderStatusUpdateSchema().load(
            request.get_json()
        )
    except ValidationError as err:
        return {"error": err.messages}, 400

    order = db.session.get(Order, order_id)

    if not order:
        return {"error": "Order not found"}, 404

    order.status = data["status"]

    db.session.commit()

    cache.clear()

    return {
        "message": "Order status updated successfully",
        "order_id": order.id,
        "status": order.status
    }, 200



@orders_bp.route("/<int:order_id>/cancel", methods=["PATCH"])
@jwt_required()
@role_required("admin", "manager")
def cancel_order(order_id):

    try:

        order = db.session.get(Order, order_id)

        if not order:
            return {
                "error": "Order not found"
            }, 404

        if order.status == "cancelled":
            return {
                "error": "Order already cancelled"
            }, 400

        if order.status != "pending":
            return {
                "error": "Only pending orders can be cancelled"
            }, 400

        for item in order.items:

            product = item.product

            product.quantity += item.quantity

            inventory_log = InventoryLog(
                user_id=get_jwt_identity(),
                product_id=product.id,
                change_type="cancel_order",
                quantity_changed=item.quantity
            )

            db.session.add(inventory_log)

        order.status = "cancelled"

        db.session.commit()

        cache.clear()

        return {
            "message": "Order cancelled successfully",
            "order_id": order.id,
            "status": order.status
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "error": "Failed to cancel order",
            "details": str(e)
        }, 500