from marshmallow import Schema, fields, validate



class RegisterSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=2, max=50)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True,
        validate=validate.Length(min=8)
    )


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        load_only=True
    )


class UserResponseSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String()
    email = fields.Email()
    role = fields.String()
    created_at = fields.DateTime()

class LoginResponseSchema(Schema):
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    user = fields.Nested(UserResponseSchema)



class User_Logout_MessageSchema(Schema):
    message = fields.String(required=True)


class RefreshResponseSchema(Schema):
    access_token = fields.String(required=True)

