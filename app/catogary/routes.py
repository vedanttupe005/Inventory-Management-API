from . import catogary_bp
from flask import request
from marshmallow import ValidationError
from app.schema.catogary_schema import CategoryCreateSchema, CategorySchema
from app.extensions import db
from app.model.catogary import Catogary

from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required


@catogary_bp.route("/", methods=["GET"])
@jwt_required()
@role_required("admin", "user",'staff', "manager")
def get_catogaries():
    catogaries = db.session.query(Catogary).all()
    return CategorySchema(many=True).dump(catogaries), 200

@catogary_bp.route("/", methods=["POST"])
@jwt_required()
@role_required("admin", "manager")
def create_catogary():
    try:
        data = CategoryCreateSchema().load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400


    category = db.session.query(Catogary).filter_by(name=data['name']).first()
    if category:
        return {"error": "Catogary with this name already exists"}, 409

    category = Catogary(
        name = data['name']

    )

    db.session.add(category)
    db.session.commit()


    return {"message": "Catogary created successfully",
            "name": category.name,
            "id" : category.id
            }, 201