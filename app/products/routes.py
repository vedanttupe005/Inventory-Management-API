from app.products import products_bp
from flask import request
from app.extensions import db
from app.model.product import Product
from app.model.catogary import Catogary
from app.schema.product_schema import ProductCreateSchema,ProductUpdateSchema, ProductResponseSchema

from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required
from marshmallow import ValidationError

@products_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin", "user",'staff', "manager")
def get_products():
    products = db.session.query(Product).all()
    return ProductResponseSchema(many=True).dump(products), 200



@products_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin","manager")
def create_product():
    try:
        data = ProductCreateSchema().load(request.get_json())
    except ValidationError as err:
        return {"error": err.messages}, 400

    product = db.session.query(Product).filter_by(name=data['name']).first()
    if product:
        return {"error": "Product with this name already exists"}, 409

    category = db.session.query(Catogary).filter_by(id=data['category_id']).first()
    if not category:
        return {"error": "Category not found, create category frist "}, 404

    product = Product(
        name = data['name'],
        description = data.get('description'),
        price = data['price'],
        quantity = data['quantity'],
        category_id = data['category_id']
    )

    db.session.add(product)
    db.session.commit()

    return {"message": "Product created successfully",
            "name": product.name,
            "id" : product.id
            }, 201