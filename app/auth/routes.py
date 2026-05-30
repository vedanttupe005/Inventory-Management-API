from app.auth import auth_bp
from marshmallow import ValidationError
from flask import request, jsonify

from app.model.user import User
from app.extensions import db
from app.schema.user_schema import RegisterSchema, LoginSchema,UserResponseSchema
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity





@auth_bp.route("/register", methods=["POST"])
def register():

    try:
        data = RegisterSchema().load(
            request.get_json()
        )

    except ValidationError as err:
        return {
            "errors": err.messages
        }, 400

    existing_user = User.query.filter_by(
        email=data["email"]
    ).first()

    if existing_user:
        return {
            "error": "Email already registered"
        }, 409

    user = User(
        username=data["username"],
        email=data["email"]
    )

    user.set_password(
        data["password"]
    )

    db.session.add(user)
    db.session.commit()

    return UserResponseSchema().dump(user), 201



@auth_bp.route("/login", methods=["POST"])
def login():

    try:
        data = LoginSchema().load(
            request.get_json()
        )

    except ValidationError as err:
        return {
            "errors": err.messages
        }, 400

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if not user:
        return {
            "error": "Invalid credentials"
        }, 401

    if not user.check_password(
        data["password"]
    ):
        return {
            "error": "Invalid credentials"
        }, 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }, 200


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    return {
        "message": "Logged out successfully"
    }, 200




