from app.extensions import db


class User(db.Model):
    id = db.column(db.integer, primary_key=True)
    username = db.column(db.string(50), nullable=False)
    email = db.column(db.string(100), nullable=False, unique=True)
    password_hash = db.column(db.string(128), nullable=False)
    role = db.column(db.string(20), nullable=False, default='user')
    created_at = db.column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())