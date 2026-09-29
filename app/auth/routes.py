from app.auth import auth_bp
from marshmallow import ValidationError
from flask import request
from flask_smorest import abort

from app.model.user import User
from app.model.token_blocklist import TokenBlocklist
from app.extensions import db,limiter
from app.schema.user_schema import RegisterSchema, LoginSchema,UserResponseSchema,LoginResponseSchema,User_Logout_MessageSchema,RefreshResponseSchema
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt





@auth_bp.route("/register", methods=["POST"])
@auth_bp.doc(
    summary="Register a new user",
    description="""
        Creates a new user account with a hashed password. 
        This endpoint is publicly accessible, and 
        rate limited to 5 requests per minute.""")
@auth_bp.arguments(RegisterSchema)
@auth_bp.response(201, UserResponseSchema)
@limiter.limit("5 per minute")
def register(data):

    existing_user = User.query.filter_by(
        email=data["email"]
    ).first()

    if existing_user:
        abort(409, message="Email already registered")

    user = User(
        username=data["username"],
        email=data["email"]
    )

    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return user



@auth_bp.route("/login", methods=["POST"])
@auth_bp.doc(
    summary="Login user",
    description="""
    Authenticates a user using their email and password.
    Returns JWT access and refresh tokens. 
    This endpoint is publicly accessible and, 
    rate limited to 5 requests per minute.""")
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, LoginResponseSchema)
@limiter.limit("5 per minute")
def login(data):

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if not user:
        abort(401, message="Invalid credentials: user not found")

    if not user.check_password(data["password"]):
        abort(401, message="Invalid credentials: incorrect password")

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
        "user": user
    }


@auth_bp.route("/logout", methods=["POST"])
@auth_bp.doc(
    summary="Logout user",
    description="""
    Logs out the authenticated user by adding the current JWT to the token blocklist. 
    Requires JWT authentication.""")
@auth_bp.response(200, User_Logout_MessageSchema)
@jwt_required()
def logout():

    jti = get_jwt()["jti"]

    blocked_token = TokenBlocklist(jti=jti)

    db.session.add(blocked_token)
    db.session.commit()

    return {
        "message": "Successfully logged out"
    }



@auth_bp.route("/refresh", methods=["POST"])
@auth_bp.doc(
    summary="Refresh access token",
    description="""
    Generates a new JWT access token using a valid refresh token.
    Requires JWT refresh authentication and,
    rate limited to 20 requests per minute.""")
@auth_bp.response(200, RefreshResponseSchema)
@jwt_required(refresh=True)
@limiter.limit("20 per minute")
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
    }



