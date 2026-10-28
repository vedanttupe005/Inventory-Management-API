import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    SQlALCHEMY_TRACK_MODIFICATIONS = False

    #caching and redis configuration
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    CACHE_REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300

    API_TITLE = "Inventory Management API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"

    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    API_SPEC_OPTIONS = {
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        },
        "security": [
            {
                "BearerAuth": []
            }
        ]
    }


class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL")
    TESTING = True
    RATELIMIT_ENABLED = False
    CACHE_TYPE = "NullCache"
