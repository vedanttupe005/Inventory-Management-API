from flask import Flask
from .extensions import db, migrate,jwt
from .config import Config
from app.model.user import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    jwt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    @app.route('/')
    def index():
        return {"message": "Welcome to the Flask API!"}

    return app