from app.extensions import db

class InventoryLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    change_type = db.Column(db.String(20), nullable=False)  # 'addition' or 'subtraction'
    quantity_changed = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

    product = db.relationship('Product', backref=db.backref('inventory_logs', lazy=True))
    user = db.relationship('User', backref=db.backref('inventory_logs', lazy=True))