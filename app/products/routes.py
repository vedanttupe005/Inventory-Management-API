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

    # Get query parameters for filtering
    search_name = request.args.get("name")

    product_obj = db.session.query(Product)
    if search_name:
        product_obj = product_obj.filter(Product.name.ilike(f"%{search_name}%"))




    # pagination
    page = request.args.get("page", default= 1, type=int)
    limit = request.args.get("limit",default=10,type=int)

    if page < 1 or limit < 1:
        return {"error": "Page and limit must be positive integers"}, 400
    if limit > 100:
        return {"error": "Limit must not exceed 100"}, 400


    pagination = product_obj.paginate(page=page, per_page=limit, error_out=False)

    products = ProductResponseSchema(many=True).dump(pagination.items)

    return {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "items": products
    }, 200


@products_bp.route("/<int:product_id>", methods=["GET"])
@jwt_required()
@role_required("admin", "user",'staff', "manager")
def get_product(product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()
    if not product:
        return {"error": "Product not found"}, 404

    return ProductResponseSchema().dump(product), 200


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




@products_bp.route("/<int:product_id>", methods=["PATCH"])
@jwt_required()
@role_required("admin","manager")
def update_product(product_id):

    product = db.session.query(Product).filter_by(id=product_id).first()
    if not product:
        return {"error": "Product not found"}, 404

    try:
        data = ProductUpdateSchema().load(request.get_json())
    except ValidationError as err:
        return {"error":err.messages},400

    if "category_id" in data:
        category = db.session.query(Catogary).filter_by(id  = data['category_id']).first()
        if not category:
            return {"error": "Category not found, create category frist "}, 404


    for key, value in data.items():
        setattr(product,key,value)

    db.session.commit()

    return {"message": "Product updated successfully",
                "name": product.name,
                "id" : product.id

            }, 200


@products_bp.route("/<int:product_id>",methods = ["DELETE"])
@jwt_required()
@role_required("admin","manager")
def delete_product(product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        return {"error":"Product not found"}, 404

    db.session.delete(product)
    db.session.commit()

    return {"message": "Product deleted successfully",
            "id": product.id,
            "name": product.name,
            "description" : product.description

            }, 200