from . import category_bp
from flask import request
from flask_smorest import abort
from marshmallow import ValidationError
from app.schema.catogary_schema import CategoryCreateSchema, CategorySchema
from app.extensions import db,cache
from app.model.catogary import Catogary

from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required


@category_bp.route("/", methods=["GET"])
@category_bp.response(200, CategorySchema(many=True))
@category_bp.doc(
    summary="Get all categories",
    description="""
        Returns all available product categories. Requires JWT authentication.""")
@jwt_required()
@role_required("admin", "user",'staff', "manager")
@cache.cached(key_prefix="categories_list", timeout=300)
def get_catogaries():
    print("cache missed")
    catogaries = db.session.query(Catogary).all()
    return catogaries




@category_bp.route("/<int:category_id>")
@category_bp.doc(
    summary="Get category by ID",
    description="""
    Returns a single category by its ID.

    Requires JWT authentication.

    Accessible by:
    - Admin
    - Manager
    - Staff
    - User
    """)
@category_bp.response(200, CategorySchema)
@jwt_required()
@role_required("admin", "user", "staff", "manager")
@cache.cached(timeout=300,key_prefix=lambda: f"category_{request.view_args['category_id']}")
def get_category(category_id):

    category = Catogary.query.get(category_id)

    if not category:
        abort(404, message="Category not found")

    print("cache missed")

    return category



@category_bp.route("/", methods=["POST"])
@category_bp.doc(
    summary="Create a category",
    description="""
        Creates a new product category. Requires JWT authentication. Accessible by Admin and Manager roles.""")
@category_bp.arguments(CategoryCreateSchema)
@category_bp.response(201, CategorySchema)
@jwt_required()
@role_required("admin", "manager")
def create_category(data):

    category = db.session.query(Catogary).filter_by(
        name=data["name"]
    ).first()

    if category:
        return {"error": "Category with this name already exists"}, 409

    category = Catogary(
        name=data["name"]
    )

    db.session.add(category)
    db.session.commit()

    # Clear category cache
    cache.delete("categories_list")
    cache.delete(f"category_{category.id}")

    return category






@category_bp.route("/<int:category_id>", methods=["PUT"])
@category_bp.doc(
    summary="Update a category",
    description="""
    Updates the name of an existing category. Requires JWT authentication. Accessible by Admin and Manager roles.""")
@category_bp.arguments(CategoryCreateSchema)
@category_bp.response(200, CategorySchema)
@jwt_required()
@role_required("admin", "manager")
def update_category(data, category_id):

    category = Catogary.query.get(category_id)

    if not category:
        return {"error": "Category not found"}, 404

    category.name = data["name"]

    db.session.commit()

    # Clear category cache
    cache.delete("categories_list")
    cache.delete(f"category_{category.id}")

    return category


@category_bp.route("/<int:category_id>", methods=["DELETE"])
@category_bp.doc(
    summary="Delete a category",
    description="Deletes a category if it has no associated products. Requires JWT authentication. Accessible by Admin role only."
)
@jwt_required()
@role_required("admin")
def delete_category(category_id):

    category = Catogary.query.get(category_id)

    if not category:
        return {
            "error": "Category not found"
        }, 404

    if category.products:
        return {
            "error": "Cannot delete category with products"
        }, 400

    db.session.delete(category)
    db.session.commit()

    # Clear category cache
    cache.delete("categories_list")
    cache.delete(f"category_{category.id}")

    return {
        "message": "Category deleted successfully"
    }, 200
