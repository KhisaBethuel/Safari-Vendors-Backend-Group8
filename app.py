from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Resource, Api
from models import *
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")

migrate = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)

api = Api(app)
CORS(app)


class Register(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type') 

        if user_type == 'buyer':
            if Buyers.query.filter_by(email=email).first():
                return make_response({"message": "Buyer with this email already exists!"}, 400)

            new_buyer = Buyers(username=username, email=email, password=password)
            db.session.add(new_buyer)
            db.session.commit()

            return make_response({"message": "Buyer registered successfully!"}, 201)

        elif user_type == 'vendor':
            if Vendors.query.filter_by(email=email).first():
                return make_response({"message": "Vendor with this email already exists!"}, 400)

            new_vendor = Vendors(username=username, email=email, password=password)
            db.session.add(new_vendor)
            db.session.commit()

            return make_response({"message": "Vendor registered successfully!"}, 201)
        
        

        return make_response({"message": "Invalid user_type!"}, 400)

api.add_resource(Register, '/register')


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user_type = data.get('user_type') 

        if user_type == 'buyer':
            buyer = Buyers.query.filter_by(email=email).first()
            if not buyer or not buyer.check_password(password):
                return make_response({"message": "Invalid buyer credentials!"}, 401)

            access_token = create_access_token(identity={"id": buyer.id, "role": "buyer"})
            return make_response({"access_token": access_token}, 200)

        elif user_type == 'vendor':
            vendor = Vendors.query.filter_by(email=email).first()
            if not vendor or not vendor.check_password(password):
                return make_response({"message": "Invalid vendor credentials!"}, 401)

            access_token = create_access_token(identity={"id": vendor.id, "role": "vendor"})
            return make_response({"access_token": access_token}, 200)

        return make_response({"message": "Invalid role!"}, 400)
    

api.add_resource(Login, '/login')


class Logout(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti'] 
        revoked_token = TokenBlocklist(jti=jti)
        db.session.add(revoked_token)
        db.session.commit()
        return make_response({"message": "Successfully logged out!"}, 200)
    
    
api.add_resource(Logout, '/logout')
    
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None 

class Product(Resource):
    def get(self):
        products = Products.query.all()
        return make_response(jsonify([product.to_dict() for product in products]), 200)

    @jwt_required()
    def post(self):
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        category = data.get('category')

        new_product = Products(name=name, price=price, category=category)
        db.session.add(new_product)
        db.session.commit()

        return make_response({"message": "Product created successfully!"}, 201)

api.add_resource(Product, '/products')

class SingleProduct(Resource):
    @jwt_required()
    def get(self, product_id):
        product = Products.query.get_or_404(product_id)
        return make_response(product.to_dict(), 200)

    @jwt_required()
    def patch(self, product_id):
        product = Products.query.get_or_404(product_id)
        data = request.get_json()

        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.category = data.get('category', product.category)

        db.session.commit()
        return make_response({"message": "Product updated successfully!"}, 200)
    
    
api.add_resource(SingleProduct, '/products/<int:product_id>')


#Home route or root page
@app.route("/")
def home():
    return "Welcome To this API generation"


if __name__ == "__main__":
    app.run(port=8083, debug=True)

    from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import logging
from models import db, User, Vendor, Product, Order, OrderItem, Review, UserSchema, OrderSchema, ReviewSchema

app = Flask(__name__)

# First Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safarivendors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'my_super_secret_key'  # Use a strong, unique secret key for production
app.json.compact = False

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
db.init_app(app)

# Home route or root page
@app.route("/")
def home():
    return "Welcome To Safari Vendors API"

# Login route
@app.route('/login', methods=['POST'])
def login():
    """Log in a user and return a JWT."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return make_response(jsonify({"error": "Email and password are required."}), 400)

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=user.id)
        return make_response(jsonify(access_token=access_token), 200)
    else:
        return make_response(jsonify({"error": "Bad email or password."}), 401)

# Create a new review
@app.route('/products/<int:product_id>/reviews', methods=['POST'])
@jwt_required()
def create_review(product_id):
    """Submit a review for a specific product."""
    current_user_id = get_jwt_identity()  # Get the ID of the current user
    data = request.json

    # Validate input
    rating = data.get('rating')
    comment = data.get('comment')

    if rating is None or comment is None:
        return make_response(jsonify({"error": "Rating and comment are required."}), 400)

    try:
        new_review = Review(user_id=current_user_id, product_id=product_id, rating=rating, comment=comment)
        db.session.add(new_review)
        db.session.commit()
        review_schema = ReviewSchema()  # Use your schema to return the newly created review
        return make_response(jsonify(review_schema.dump(new_review)), 201)
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while creating the review."}), 500)

# Create a new order (checkout)
@app.route('/checkout', methods=['POST'])
@jwt_required()
def create_order():
    """Create a new order for the current user."""
    current_user_id = get_jwt_identity()  # Get the ID of the current user
    data = request.json

    product_ids = data.get('product_ids')

    if not product_ids or not isinstance(product_ids, list):
        return make_response(jsonify({"error": "A list of Product IDs is required."}), 400)

    try:
        # Validate product IDs
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        if len(products) != len(product_ids):
            return make_response(jsonify({"error": "Some products are invalid."}), 400)

        # Create the order
        order = Order(user_id=current_user_id)
        db.session.add(order)
        db.session.commit()  # Commit to get the order ID

        # Add order items
        for product in products:
            order_item = OrderItem(order_id=order.id, product_id=product.id)
            db.session.add(order_item)

        db.session.commit()  # Commit the order items
        order_schema = OrderSchema()
        return make_response(order_schema.dump(order), 201)
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while creating the order."}), 500)

# Get all orders for the current user
@app.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    """Fetch and return a list of orders for the current user."""
    current_user_id = get_jwt_identity()  # Get the ID of the current user

    try:
        orders = Order.query.filter_by(user_id=current_user_id).all()
        order_schema = OrderSchema(many=True)
        return make_response(jsonify(order_schema.dump(orders)), 200)
    except Exception as e:
        logger.error(f"Error fetching orders: {str(e)}")
        return make_response(jsonify({"error": "An error occurred while fetching orders."}), 500)

if __name__ == "__main__":
    app.run(port=5500, debug=True)
