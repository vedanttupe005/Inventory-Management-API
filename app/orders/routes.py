from app.orders import orders_bp
from app.schema.order_schema import OrderCreateSchema, OrderResponseSchema
from marshmallow import ValidationError
from app.model import Order, OrderItems, Product
from app.extensions import db
from flask import request

from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required


@orders_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin", "user", "staff", "manager")
def create_order():
    try:
        data = OrderCreateSchema().load(request.get_json())
    except ValidationError as err:
        return {"error": err.messages}, 400

    order_items = []
    total_amount = 0
    for item in data['items']:
        product = db.session.query(Product).filter_by(id = item['product_id']).first()
        if not product:
            return {"erroe": f"Product with id {item['product_id']} not found"}, 404
        if product.quantity < item['quantity']:
            return {"error": f"Not enough quantity for product {product.name}"}, 400

        total_amount += product.price * item['quantity']
        order_items.append({
            "product_id": item['product_id'],
            "quantity": item['quantity'],
            "price": product.price
        })



    order = Order(
        user_id = get_jwt_identity(),
        total_amount=total_amount
    )
    db.session.add(order)
    db.session.flush()# to get the order id before commit


    for item in order_items:
        product = db.session.query(Product).filter_by(id = item['product_id']).first()
        order_item = OrderItems(
            order_id = order.id,
            product_id = item['product_id'],
            quantity = item['quantity'],
            price = item['price']
        )
        db.session.add(order_item)
        product.quantity -= item['quantity']

    db.session.commit()

    return {"message": "Order created successfully",
            "order_id": order.id,
            "total_amount": order.total_amount
            }, 201

