from flask import Flask, make_response, request
from flask_migrate import Migrate
from flask_restful import Resource, Api
from models import *
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt
from flask_cors import CORS
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY")

migrate = Migrate(app, db)
db.init_app(app)
jwt = JWTManager(app)
db = SQLAlchemy(app)

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
            if Buyer.query.filter_by(email=email).first():
                return make_response({"message": "Buyer with this email already exists!"}, 400)

            new_buyer = Buyer(username=username, email=email)
            new_buyer.password = password
            db.session.add(new_buyer)
            db.session.commit()

            return make_response({"message": "Buyer registered successfully!"}, 201)

        elif user_type == 'vendor':
            if Vendor.query.filter_by(email=email).first():
                return make_response({"message": "Vendor with this email already exists!"}, 400)

            new_vendor = Vendor(username=username, email=email)
            new_vendor.password = password
            db.session.add(new_vendor)
            db.session.commit()

            return make_response({"message": "Vendor registered successfully!"}, 201)
        
        elif user_type == 'both':
            if Buyer.query.filter_by(email=email).first() or Vendor.query.filter_by(email=email).first():
                return make_response({"message": "User with this email already exists!"}, 400)

            new_buyer = Buyer(username=username, email=email)
            new_buyer.password = password
            new_vendor = Vendor(username=username, email=email)
            new_vendor.password = password
            db.session.add(new_buyer)
            db.session.add(new_vendor)
            db.session.commit()
            return make_response({"message": "Buyer and Vendor registered successfully!"}, 201)

        return make_response({"message": "Invalid user_type!"}, 400)

api.add_resource(Register, '/register')


class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        # buyer
        buyer = Buyer.query.filter_by(email=email).first()
        if buyer and buyer.check_password(password):
            access_token = create_access_token(identity={"id": buyer.id, "user_type": "buyer"})
            refresh_token = create_refresh_token(identity={"id": buyer.id, "user_type": "buyer"})
            return make_response({"access_token": access_token, "refresh_token": refresh_token}, 200)

        # vendor 
        vendor = Vendor.query.filter_by(email=email).first()
        if vendor and vendor.check_password(password):
            access_token = create_access_token(identity={"id": vendor.id, "user_type": "vendor"})
            refresh_token = create_refresh_token(identity={"id": vendor.id, "user_type": "vendor"})
            return make_response({"access_token": access_token, "refresh_token": refresh_token}, 200)

        # user with both roles
        general_user = Buyer.query.filter_by(email=email).first()
        if general_user and general_user.check_password(password):
            access_token = create_access_token(identity={"id": general_user.id, "user_type": "both"})
            refresh_token = create_refresh_token(identity={"id": general_user.id, "user_type": "both"})
            return make_response({"access_token": access_token, "refresh_token": refresh_token}, 200)


        return make_response({"message": "Invalid username or password!"}, 400)
    

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
        products = Product.query.all()
        return make_response(jsonify([product.to_dict() for product in products]), 200)

    @jwt_required()
    def post(self):
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        category = data.get('category')
        image_url = data.get("image_url")

        new_product = Product(name=name, price=price, category=category, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()

        return make_response({"message": "Product created successfully!"}, 201)

api.add_resource(Product, '/products')

class SingleProduct(Resource):
    @jwt_required()
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        return make_response(product.to_dict(), 200)

    @jwt_required()
    def patch(self, product_id):
        product = Product.query.get_or_404(product_id)
        data = request.get_json()

        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.category = data.get('category', product.category)
        product.image_url = data.get('image_url', product.image_url)
        
        db.session.commit()
        return make_response({"message": "Product updated successfully!"}, 200)
    
    @jwt_required()
    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return make_response({"message": "Product deleted successfully!"}, 200)
    
api.add_resource(SingleProduct, '/products/<int:product_id>')

class Cart(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt()['sub']['id']
        cart = Cart.query.filter_by(buyer_id=user_id).first()
        if cart:
            return make_response(cart.to_dict(), 200)
        return make_response({"message": "Cart not found!"}, 404)

    @jwt_required()
    def post(self):
        user_id = get_jwt()['sub']['id']
        cart = Cart(buyer_id=user_id)
        db.session.add(cart)
        db.session.commit()
        return make_response({"message": "Cart created successfully!"}, 201)

api.add_resource(Cart, '/cart')

class ReviewResource(Resource):
    @jwt_required()
    def post(self, product_id):
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment')

        user_id = get_jwt()['sub']['id']
        vendor = Vendors.query.filter_by(id=user_id).first()
        buyer = Buyers.query.filter_by(id=user_id).first()

        if vendor:
            return make_response({"message": "Vendors cannot leave reviews!"}, 403)

        new_review = Review(rating=rating, comment=comment, product_id=product_id, buyer_id=user_id)
        db.session.add(new_review)
        db.session.commit()
        return make_response({"message": "Review created successfully!"}, 201)

api.add_resource(ReviewResource, '/products/<int:product_id>/reviews')


#Home route or root page
@app.route("/")
def home():
    return "Welcome To this API generation"


if __name__ == "__main__":
    app.run(port=8083, debug=True)