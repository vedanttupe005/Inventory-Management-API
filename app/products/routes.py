from app.products import products_bp
from flask import request
from app.extensions import db,cache,limiter
from app.model.product import Product
from app.model.catogary import Catogary
from app.model.inventory_log import InventoryLog
from app.schema.product_schema import ProductCreateSchema,ProductUpdateSchema, ProductResponseSchema

from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required
from marshmallow import ValidationError

@products_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin", "user",'staff', "manager")
@cache.cached(timeout=300, query_string=True)
def get_products():
    print("cache missed")
    # Get query parameters for filtering
    search_name = request.args.get("name")
    category_name = request.args.get("category")
    category_id = request.args.get("category_id", type=int)
    price_lt = request.args.get("price_lt", type=float)#lt means less than
    price_gt = request.args.get("price_gt", type=float)#gt means greater than
    quantity_lt = request.args.get("quantity_lt", type=int)
    quantity_gt = request.args.get("quantity_gt", type=int)


    # filter mapping
    product_obj = db.session.query(Product)

    if search_name  is not None:
        product_obj = product_obj.filter(Product.name.ilike(f"%{search_name}%"))
    if category_name is not None:
        product_obj = product_obj.join(Catogary).filter(Catogary.name.ilike(f"%{category_name}%"))
    if category_id is not None:
        product_obj = product_obj.filter(Product.category_id == category_id)
    if price_lt is not None:
        product_obj = product_obj.filter(Product.price <= price_lt)
    if price_gt is not None:
        product_obj = product_obj.filter(Product.price >= price_gt)
    if quantity_lt is not None:
        product_obj = product_obj.filter(Product.quantity <= quantity_lt)
    if quantity_gt is not None:
        product_obj = product_obj.filter(Product.quantity >= quantity_gt)


    # sorting
    sort = request.args.get("sort")

    if sort :
        decending = sort.startswith("-") # if the sort field starts with "-" it means we want to sort in descending order
        sort_field = sort.lstrip("-")

        allowed_sort_fielda = {
            "name": Product.name,
            "price": Product.price,
            "quantity": Product.quantity,
            "category": Product.category_id,
            "created_at": Product.created_at,
            "updated_at": Product.updated_at
        }

        sort_column = allowed_sort_fielda.get(sort_field)

        if sort_column is not None:
            if decending:
                sort_column = sort_column.desc()
            product_obj = product_obj.order_by(sort_column)



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
@cache.cached(timeout=300 ,query_string=True)
def get_product(product_id):
    print("cache missed")
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
    db.session.flush()

    inventory_log = InventoryLog(
        user_id = get_jwt_identity(),
        product_id = product.id,
        change_type = "product created",
        quantity_changed = product.quantity

    )

    db.session.add(inventory_log)
    db.session.commit()

    cache.clear()

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
        category = db.session.query(Catogary).filter_by(id = data['category_id']).first()
        if not category:
            return {"error": "Category not found, create category frist "}, 404

    if "quantity" in data:
        quantity_change = data['quantity'] - product.quantity

        if quantity_change != 0:
            inventory_log = InventoryLog(
                user_id = get_jwt_identity(),
                product_id = product.id,
                change_type = "stock adjustment",
                quantity_changed = quantity_change

            )

        db.session.add(inventory_log)

    for key, value in data.items():
        setattr(product,key,value)

    db.session.commit()

    cache.clear()

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

    cache.clear()

    return {"message": "Product deleted successfully",
            "id": product.id,
            "name": product.name,
            "description" : product.description

            }, 200