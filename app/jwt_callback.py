
from app.extensions import jwt
from app.model.token_blocklist import TokenBlocklist


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header,jwt_payload):

    jti = jwt_payload["jti"]

    token = TokenBlocklist.query.filter_by(
        jti=jti
    ).first()

    return token is not None