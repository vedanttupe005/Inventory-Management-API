from app.orders import orders_bp
from app.schema.order_schema import OrderCreateSchema, OrderResponseSchema,OrderStatusUpdateSchema,OrderPaginationSchema
from marshmallow import ValidationError
from app.model import Order, OrderItems, Product, InventoryLog
from app.extensions import db, cache,limiter
from flask import request
from flask_smorest import abort
from werkzeug.exceptions import HTTPException

from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils.decorators import role_required


@orders_bp.route("/", methods=["POST"])
@orders_bp.doc(
    summary="Create an order",
    description="""
        Creates a new order,
        updates product inventory,
        and records inventory logs. 
        
        Requires JWT authentication. 
        Roles allowed: Admin, User, Staff, Manager.""")
@orders_bp.arguments(OrderCreateSchema)
@orders_bp.response(201, OrderResponseSchema)
@jwt_required()
@role_required("admin", "user", "staff", "manager")
@limiter.limit("10 per minute")
def create_order(data):

    try:
        total_amount = 0
        validated_items = []
        seen_products = set()

        # Validation Phase
        for item in data["items"]:

            if item["product_id"] in seen_products:
                abort(400, message=f"Duplicate product_id {item['product_id']} in order items")


            seen_products.add(item["product_id"])

            product = Product.query.get(item["product_id"])

            if not product:
                abort(400, message=f"Product with id {item['product_id']} does not exist")

            if item["quantity"] <= 0:
                abort(400, message=f"Quantity for product {product.name} must be greater than 0")

            if product.quantity < item["quantity"]:
                abort(400, message=f"Insufficient stock for product {product.name}. Available: {product.quantity}, Requested: {item['quantity']}")

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
        db.session.flush()

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

        cache.clear()

        return order

    except HTTPException:
        raise

    except Exception as e:
        db.session.rollback()

        abort(500, message=f"Failed to create order: {str(e)}")



@orders_bp.route("/<int:order_id>", methods=["GET"])
@orders_bp.doc(
    summary="Get order by ID",
    description="""
        Returns the order associated with the specified ID. 
        
        Requires JWT authentication. Roles allowed: Admin, Manager, Staff, User.
        Admins and Managers can view any order, 
        while Staff and Users can only view their own orders.""")
@orders_bp.response(200, OrderResponseSchema)
@jwt_required()
@role_required("admin", "manager", "staff", "user")
def get_order(order_id):

    order = db.session.query(Order).filter_by(id=order_id).first()

    if not order:
        abort(404, message="Order not found")


    role = get_jwt()["role"]


    if role not in ["admin", "manager"]:
        if order.user_id != int(get_jwt_identity()):
            abort(403, message="Forbidden: You are not allowed to access this order")

    return order





@orders_bp.route("/", methods=["GET"])
@orders_bp.doc(
    summary="Get all orders",
    description="""
        Returns a paginated list of orders. 
        
        Requires JWT authentication. Roles allowed: Admin, Manager, Staff, User.
        Admins and Managers can view all orders, 
        while Staff and Users can only view their own orders.""",
    parameters=[
        {
            "in": "query",
            "name": "page",
            "schema": {
                "type": "integer",
                "default": 1
            },
            "description": "Page number."
        },
        {
            "in": "query",
            "name": "limit",
            "schema": {
                "type": "integer",
                "default": 10
            },
            "description": "Number of orders per page (maximum 100)."
        }
    ]
)
@orders_bp.response(200, OrderPaginationSchema)
@jwt_required()
@role_required("admin", "manager", "staff", "user")
def get_orders():

    role = get_jwt()["role"]

    query = Order.query

    if role not in ["admin", "manager"]:
        query = query.filter_by(
            user_id=get_jwt_identity()
        )

    query = query.order_by(
        Order.created_at.desc()
    )

    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    if page < 1 or limit < 1:
        abort(400, message="Page and limit must be greater than 0")

    if limit > 100:
        abort(400, message="Limit must not exceed 100")

    pagination = query.paginate(
        page=page,
        per_page=limit,
        error_out=False
    )

    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "items": pagination.items
    }




@orders_bp.route("/<int:order_id>/status", methods=["PATCH"])
@orders_bp.doc(
    summary="Update order status",
    description="""
        Updates the status of an existing order.
        Requires JWT authentication. Role allowed : admin, manager.
"pending",
"processing",
"completed",
"cancelled"
        """)
@orders_bp.arguments(OrderStatusUpdateSchema)
@orders_bp.response(200, OrderResponseSchema)
@jwt_required()
@role_required("admin", "manager")
def update_order_status(data, order_id):

    order = db.session.get(Order, order_id)

    if not order:
        abort(404, message="Order not found")

    order.status = data["status"]

    db.session.commit()

    cache.clear()

    return order



@orders_bp.route("/<int:order_id>/cancel", methods=["PATCH"])
@orders_bp.doc(
    summary="Cancel an order",
    description="""Cancels a pending order,
                
                restores product inventory, and records inventory logs. 
                
                Requires JWT authentication. 
                Roles allowed: Admin, Manager.""")
@orders_bp.response(200, OrderResponseSchema)
@jwt_required()
@role_required("admin", "manager")
def cancel_order(order_id):

    try:

        order = db.session.get(Order, order_id)

        if not order:
            abort(404, message="Order not found")

        if order.status == "cancelled":
            abort(400, message="Order is already cancelled")

        if order.status != "pending":
            abort(400, message="Only pending orders can be cancelled")

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

        return order

    except HTTPException:
        raise

    except Exception as e:

        db.session.rollback()

        abort(500, message=f"Failed to cancel order: {str(e)}")