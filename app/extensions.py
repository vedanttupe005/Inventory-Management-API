from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache



jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()

