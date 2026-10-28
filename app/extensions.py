from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_smorest import Api
from dotenv import load_dotenv
import os
load_dotenv()



jwt = JWTManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()

limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv('RATELIMIT_STORAGE_URI'))  # Use Redis for rate limiting

api = Api()