from marshmallow import Schema, fields, validate


class OrderItemSchema(Schema):
    product_id = fields.Integer(required=True)

    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )


class OrderCreateSchema(Schema):
    items = fields.List(
        fields.Nested(OrderItemSchema),
        required=True,
        validate=validate.Length(min=1)
    )


class OrderItemResponseSchema(Schema):
    id = fields.Integer(dump_only=True)

    product_id = fields.Integer()

    quantity = fields.Integer()

    price = fields.Float()


class OrderResponseSchema(Schema):
    id = fields.Integer(dump_only=True)

    user_id = fields.Integer()

    total_amount = fields.Float()

    status = fields.String()

    created_at = fields.DateTime()

    updated_at = fields.DateTime()

    items = fields.List(
        fields.Nested(OrderItemResponseSchema)
    )


class OrderStatusUpdateSchema(Schema):
    status = fields.String(
        required=True,
        validate=validate.OneOf([
            "pending",
            "processing",
            "completed",
            "cancelled"
        ])
    )


class OrderPaginationSchema(Schema):
    page = fields.Integer()
    per_page = fields.Integer()
    total = fields.Integer()
    pages = fields.Integer()
    items = fields.List(fields.Nested(OrderResponseSchema))