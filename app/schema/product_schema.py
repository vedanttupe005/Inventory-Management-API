from marshmallow import Schema, fields, validate


class ProductCreateSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    description = fields.String()

    price = fields.Float(
        required=True,
        validate=validate.Range(min=0)
    )

    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=0)
    )

    category_id = fields.Integer(required=True)


class ProductUpdateSchema(Schema):
    name = fields.String(
        validate=validate.Length(min=2, max=100)
    )

    description = fields.String()

    price = fields.Float(
        validate=validate.Range(min=0)
    )

    quantity = fields.Integer(
        validate=validate.Range(min=0)
    )

    category_id = fields.Integer()


class ProductResponseSchema(Schema):
    id = fields.Integer(dump_only=True)

    name = fields.String()

    description = fields.String()

    price = fields.Float()

    quantity = fields.Integer()

    category_id = fields.Integer()

    created_at = fields.DateTime()

    updated_at = fields.DateTime()