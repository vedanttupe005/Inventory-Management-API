from flask import Flask
from .extensions import db, migrate,jwt
from .config import Config
from app.model.user import User
from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app import jwt_callback

    from app.auth import auth_bp
    from app.catogary import catogary_bp

    app.register_blueprint(catogary_bp)
    app.register_blueprint(auth_bp)


    @app.route('/')
    @jwt_required()
    @role_required( "user","staff", "manager", "admin")
    def index():
        return {"message": "Welcome to the Flask API!"}

    return app