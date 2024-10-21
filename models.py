from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

#association table for vendor and products
vendor_products = db.Table('vendor_products',
    db.Column('vendor_id', db.Integer, db.ForeignKey('vendors.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)


cart_products = db.Table('cart_products',
    db.Column('cart_id', db.Integer, db.ForeignKey('carts.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)

class Buyers(db.Model, SerializerMixin):
    
    __tablename__ = "buyers"
    
    serialize_rules = ('-password', '-orders.buyer', '-cart.buyer') 
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255))
    
    
    @validates('password')
    def set_password(self, key, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    
    #relationship with an order
    orders = db.relationship("Order", back_populates="buyer", lazy=True)
    
    #relationship with cart
    cart = db.relationship('Cart', back_populates='buyer', lazy=True)
    
    
class Vendors(db.Model, SerializerMixin):
    __tablename__ = "vendors"
    
    serialize_rules = ('-password', '-reviews.vendor', '-products.vendors', '-orders.vendor')
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255))
    
    
    @validates('password')
    def set_password(self, key, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
    #relationship with a product(many to many)

    products = db.relationship('Product', secondary=vendor_products, back_populates='vendors', lazy=True)
    
    #relationship with an order
    orders = db.relationship("Order", back_populates="vendor", lazy=True)
    # a relationship with the reviews
    reviews = db.relationship("Review", back_populates="vendor", lazy=True)
    

class Products(db.Model, SerializerMixin):
    __tablename__ = "products"
    
    serialize_rules = ('-vendors.products', '-reviews.product') 
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    
    
    
    # Relationship with vendor
    vendors = db.relationship("Vendors", secondary=vendor_products, back_populates="products")
    reviews = db.relationship("Review", back_populates="product", lazy=True)
    
    
    
    
class Cart(db.Model, SerializerMixin):
    __tablename__ = "carts"
    
    serialize_rules = ('-buyer.cart', '-products.carts')
    
    id = db.Column(db.Integer, primary_key=True)
    
    
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=False)
    
    products = db.relationship('Products', secondary=cart_products, back_populates='carts', lazy=True)
    

class Order(db.Model, SerializerMixin):
    
    __tablename__ = "orders"
    
    serialize_rules = ('-buyer.orders', '-vendor.orders')
    
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('buyers.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    
    buyer = db.relationship('Buyers', back_populates='orders', lazy=True)
    vendor = db.relationship('Vendors', back_populates='orders', lazy=True)
    
    
class Review(db.Model, SerializerMixin):
    
    __tablename__ = "reviews"
    
    serialize_rules = ('-vendor.reviews', '-product.reviews')

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    
    product = db.relationship('Products', back_populates='reviews', lazy=True)
    vendor = db.relationship('Vendors', back_populates='reviews', lazy=True)
    
    
class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())