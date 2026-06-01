from functools import wraps

from flask_jwt_extended import get_jwt


def role_required(*allowed_roles):

    def decorator(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):

            claims = get_jwt()

            user_role = claims.get("role")

            if user_role not in allowed_roles:
                return {
                    "error": "Forbidden you are not allowed to access this resource"
                }, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator