from marshmallow import Schema, fields, validate


class CategoryCreateSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)

    name = fields.String()

    created_at = fields.DateTime(dump_only=True)