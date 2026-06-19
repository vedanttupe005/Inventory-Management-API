from app.auth import auth_bp
from marshmallow import ValidationError
from flask import request

from app.model.user import User
from app.model.token_blocklist import TokenBlocklist
from app.extensions import db,limiter
from app.schema.user_schema import RegisterSchema, LoginSchema,UserResponseSchema
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt





@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
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
@limiter.limit("5 per minute")
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
            "error": "Invalid credentials user not found"
        }, 401

    if not user.check_password(data["password"]):
        return {
            "error": "Invalid credentials incorrect password"
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

    jti = get_jwt()["jti"]

    blocked_token = TokenBlocklist(
        jti=jti
    )

    db.session.add(
        blocked_token
    )

    db.session.commit()

    return {
        "message":
            "Successfully logged out"
    }, 200



@auth_bp.route("/refresh",methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    return {
        "access_token": access_token

    }, 200



