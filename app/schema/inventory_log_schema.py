from marshmallow import Schema, fields, validate


class InventoryUpdateSchema(Schema):
    change_type = fields.String(
        required=True,
        validate=validate.OneOf(
            ["addition", "subtraction"]
        )
    )

    quantity_changed = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )


class InventoryLogResponseSchema(Schema):
    id = fields.Integer(dump_only=True)

    user_id = fields.Integer()

    product_id = fields.Integer()

    change_type = fields.String()

    quantity_changed = fields.Integer()

    timestamp = fields.DateTime()