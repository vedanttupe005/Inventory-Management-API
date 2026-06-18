from flask import Flask
from .extensions import db, migrate,jwt,cache
from .config import Config
from app.model.user import User
from flask_jwt_extended import jwt_required
from app.utils.decorators import role_required


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    #because we want to return the json in the order we defined in the schema not in alphabetic order
    app.json.sort_keys = False

    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)


    from app import jwt_callback

    from app.auth import auth_bp
    from app.catogary import category_bp
    from app.products import products_bp
    from app.orders import orders_bp
    from app.inventory import inventory_bp

    app.register_blueprint(inventory_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(auth_bp)


    @app.route('/')
    @jwt_required()
    @role_required( "user","staff", "manager", "admin")
    def index():
        return {"message": "Welcome to the Flask API!"}



    @app.route("/cache-test")
    def cache_test():
        cache.set("my_key", "hello redis")

        return {
            "value": cache.get("my_key")
        }

    return app