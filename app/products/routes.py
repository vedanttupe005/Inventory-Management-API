from app.products import products_bp
from flask import request
from flask_smorest import abort
from app.extensions import db,cache,limiter
from app.model.product import Product
from app.model.catogary import Catogary
from app.model.inventory_log import InventoryLog
from app.schema.product_schema import ProductCreateSchema,ProductUpdateSchema, ProductResponseSchema,ProductPaginationSchema,Product_Delete_MessageSchema

from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.decorators import role_required
from marshmallow import ValidationError

@products_bp.route("/", methods=["GET"])
@products_bp.doc(
    summary="Get all products",
    description="""
    Returns a paginated list of products. Supports searching, filtering, sorting, and pagination. Requires JWT authentication.""",
    parameters=[
        {
            "in": "query",
            "name": "name",
            "schema": {"type": "string"},
            "description": "Search products by name."
        },
        {
            "in": "query",
            "name": "category",
            "schema": {"type": "string"},
            "description": "Filter products by category name."
        },
        {
            "in": "query",
            "name": "category_id",
            "schema": {"type": "integer"},
            "description": "Filter products by category ID."
        },
        {
            "in": "query",
            "name": "price_lt",
            "schema": {"type": "number"},
            "description": "Return products with price less than or equal to this value."
        },
        {
            "in": "query",
            "name": "price_gt",
            "schema": {"type": "number"},
            "description": "Return products with price greater than or equal to this value."
        },
        {
            "in": "query",
            "name": "quantity_lt",
            "schema": {"type": "integer"},
            "description": "Return products with quantity less than or equal to this value."
        },
        {
            "in": "query",
            "name": "quantity_gt",
            "schema": {"type": "integer"},
            "description": "Return products with quantity greater than or equal to this value."
        },
        {
            "in": "query",
            "name": "sort",
            "schema": {"type": "string"},
            "description": "Sort by name, price, quantity, category, created_at, or updated_at. Prefix with '-' for descending order."
        },
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
            "description": "Number of products per page (maximum 100)."
        }
    ]
)
@products_bp.response(200, ProductPaginationSchema)
@jwt_required()
@role_required("admin", "user", "staff", "manager")
@cache.cached(timeout=300, query_string=True)
def get_products():

    print("cache missed")

    # Get query parameters for filtering
    search_name = request.args.get("name")
    category_name = request.args.get("category")
    category_id = request.args.get("category_id", type=int)
    price_lt = request.args.get("price_lt", type=float)
    price_gt = request.args.get("price_gt", type=float)
    quantity_lt = request.args.get("quantity_lt", type=int)
    quantity_gt = request.args.get("quantity_gt", type=int)

    # Filter mapping
    product_obj = db.session.query(Product)

    if search_name is not None:
        product_obj = product_obj.filter(Product.name.ilike(f"%{search_name}%"))

    if category_name is not None:
        product_obj = product_obj.join(Catogary).filter(
            Catogary.name.ilike(f"%{category_name}%")
        )

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

    # Sorting
    sort = request.args.get("sort")

    if sort:
        descending = sort.startswith("-")
        sort_field = sort.lstrip("-")

        allowed_sort_fields = {
            "name": Product.name,
            "price": Product.price,
            "quantity": Product.quantity,
            "category": Product.category_id,
            "created_at": Product.created_at,
            "updated_at": Product.updated_at
        }

        sort_column = allowed_sort_fields.get(sort_field)

        if sort_column is not None:
            if descending:
                sort_column = sort_column.desc()

            product_obj = product_obj.order_by(sort_column)

    # Pagination
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    if page < 1 or limit < 1:
        abort(http_status_code=400, message="Page and limit must be greater than 0")

    if limit > 100:
        abort(http_status_code=400, message="Limit must be less than or equal to 100")

    pagination = product_obj.paginate(
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





@products_bp.route("/<int:product_id>", methods=["GET"])
@products_bp.doc(
    summary="Get product by ID",
    description="""
        Returns the product associated with the specified ID. Requires JWT authentication.""")
@products_bp.response(200, ProductResponseSchema)
@jwt_required()
@role_required("admin", "user", "staff", "manager")
@cache.cached(timeout=300, query_string=True)
def get_product(product_id):

    print("cache missed")

    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        abort(http_status_code=404, message="Product not found")

    return product




@products_bp.route("/", methods=["POST"])
@products_bp.doc(
    summary="Create a product",
    description="""
        Creates a new product and records the initial inventory log. Requires JWT authentication. Accessible by Admin and Manager roles.""")
@products_bp.arguments(ProductCreateSchema)
@products_bp.response(201, ProductResponseSchema)
@jwt_required()
@role_required("admin", "manager")
def create_product(data):

    product = db.session.query(Product).filter_by(
        name=data["name"]
    ).first()

    if product:
        abort(http_status_code=409, message="Product with this name already exists")

    category = db.session.query(Catogary).filter_by(
        id=data["category_id"]
    ).first()

    if not category:
        abort(http_status_code=404, message="Category not found. Create the category first.")

    product = Product(
        name=data["name"],
        description=data.get("description"),
        price=data["price"],
        quantity=data["quantity"],
        category_id=data["category_id"]
    )

    db.session.add(product)
    db.session.flush()

    inventory_log = InventoryLog(
        user_id=get_jwt_identity(),
        product_id=product.id,
        change_type="product created",
        quantity_changed=product.quantity
    )

    db.session.add(inventory_log)
    db.session.commit()

    cache.clear()

    return product




@products_bp.route("/<int:product_id>", methods=["PATCH"])
@products_bp.doc(
    summary="Update a product",
    description="""
        Updates one or more product fields. Stock quantity changes are recorded in the inventory log. Requires JWT authentication. Accessible by Admin and Manager roles.""")
@products_bp.arguments(ProductUpdateSchema)
@products_bp.response(200, ProductResponseSchema)
@jwt_required()
@role_required("admin", "manager")
def update_product(data, product_id):

    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        abort(http_status_code=404, message="Product not found")

    if "category_id" in data:
        category = db.session.query(Catogary).filter_by(
            id=data["category_id"]
        ).first()

        if not category:
            abort(http_status_code=404, message="Category not found. Create the category first.")

    if "quantity" in data:
        quantity_change = data["quantity"] - product.quantity

        if quantity_change != 0:
            inventory_log = InventoryLog(
                user_id=get_jwt_identity(),
                product_id=product.id,
                change_type="stock adjustment",
                quantity_changed=quantity_change
            )

            db.session.add(inventory_log)

    for key, value in data.items():
        setattr(product, key, value)

    db.session.commit()

    cache.clear()

    return product


@products_bp.route("/<int:product_id>", methods=["DELETE"])
@products_bp.doc(
    summary="Delete a product",
    description="Deletes the specified product. Requires JWT authentication. Accessible by Admin and Manager roles.",
    parameters=[
        {
            "in": "path",
            "name": "product_id",
            "schema": {"type": "integer"},
            "required": True,
            "description": "Unique ID of the product."
        }
    ]
)
@products_bp.response(200, Product_Delete_MessageSchema)
@jwt_required()
@role_required("admin", "manager")
def delete_product(product_id):

    product = db.session.query(Product).filter_by(id=product_id).first()

    if not product:
        return {"error": "Product not found"}, 404

    db.session.delete(product)
    db.session.commit()

    cache.clear()

    return {
        "message": "Product deleted successfully"
    }