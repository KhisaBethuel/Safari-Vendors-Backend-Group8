from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Buyers(db.Model, SerializerMixin):
    
    __tablename__ = "buyers"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50))
    
    
    @validates('password')
    def set_password(self, key, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    #relationship with a review
    
    #relationship with an order
    
    #relationship with cart

class Vendors(db.Model, SerializerMixin):
    __tablename__ = "vendors"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50))
    
    
    @validates('password')
    def set_password(self, key, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    #relationship with a product(many to many)
    
    #relationship with an order
    
    
class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())