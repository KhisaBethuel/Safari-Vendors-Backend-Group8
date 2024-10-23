from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
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

db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

CORS(app)


@app.route('/register', methods=['POST'])
def register():
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



@app.route('/login', methods=['POST'])
def login():
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
    



@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti'] 
    revoked_token = TokenBlocklist(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()
    return make_response({"message": "Successfully logged out!"}, 200)
    
    

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None 

@app.route('/products', methods=['GET', 'POST'])
@jwt_required()
def products():
    if request.method == "GET":
        products = Product.query.all()
        return make_response(jsonify([product.to_dict() for product in products]), 200)

    
    elif request.method == "POST":
        data = request.get_json()
        name = data.get('name')
        price = data.get('price')
        category = data.get('category')
        image_url = data.get("image_url")

        new_product = Product(name=name, price=price, category=category, image_url=image_url)
        db.session.add(new_product)
        db.session.commit()

        return make_response({"message": "Product created successfully!"}, 201)


@app.route('/products/<int:product_id>', methods=['GET', 'PATCH', 'DELETE'])
@jwt_required()
def single_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    if request.method == "GET":
        return make_response(product.to_dict(), 200)

    
    elif request.method == "PATCH":
        data = request.get_json()

        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        product.category = data.get('category', product.category)
        product.image_url = data.get('image_url', product.image_url)
        
        db.session.commit()
        return make_response({"message": "Product updated successfully!"}, 200)
    

    elif request.method == "DELETE":
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return make_response({"message": "Product deleted successfully!"}, 200)
    

@app.route('/cart', methods=['GET', 'POST', "PATCH", "DELETE"])
@jwt_required()
def cart():
    user_id = get_jwt()['sub']['id']
    
    if request.method == "GET":
        cart = Cart.query.filter_by(buyer_id=user_id).first()
        if cart:
            return make_response(cart.to_dict(), 200)
        return make_response({"message": "Cart not found!"}, 404)

    
    elif request.method == "POST":
        cart = Cart(buyer_id=user_id)
        db.session.add(cart)
        db.session.commit()
        return make_response({"message": "Cart created successfully!"}, 201)
    
    elif request.method == "PATCH":
        cart = Cart.query.filter_by(buyer_id=user_id).first()
        if not cart:
            return make_response({"message": "Cart not found!"}, 404)

        data = request.get_json()
        product_ids = data.get('product_ids', [])

        
        cart.products.clear()  
                
        
        for product_id in product_ids:
            product = Product.query.get(product_id)
            if product:
                cart.products.append(product)

        db.session.commit()
        return make_response({"message": "Cart updated successfully!"}, 200)

    
    elif request.method == "DELETE":
        cart = Cart.query.filter_by(buyer_id=user_id).first()
        if not cart:
            return make_response({"message": "Cart not found!"}, 404)

        db.session.delete(cart)
        db.session.commit()
        return make_response({"message": "Cart deleted successfully!"}, 200)
    
@app.route('/orders', methods=['GET', 'POST'])
@jwt_required()
def orders():
    user_id = get_jwt()['sub']['id']

    if request.method == "GET":
        orders = Order.query.filter_by(buyer_id=user_id).all()
        return make_response([order.to_dict() for order in orders], 200)

    elif request.method == "POST":
        data = request.get_json()
        vendor_id = data.get('vendor_id')
        total_price = data.get('total_price')

        new_order = Order(buyer_id=user_id, vendor_id=vendor_id, total_price=total_price)
        db.session.add(new_order)
        db.session.commit()
        return make_response({"message": "Order created successfully!", "order": new_order.to_dict()}, 201)
    
@app.route('/orders/<int:order_id>', methods=['DELETE'])
@jwt_required()
def order(order_id):
    user_id = get_jwt()['sub']['id']

    order = Order.query.filter_by(id=order_id, buyer_id=user_id).first()
    if not order:
        return make_response({"message": "Order not found!"}, 404)

    db.session.delete(order)
    db.session.commit()
    return make_response({"message": "Order deleted successfully!"}, 200)
    



@app.route('/products/<int:product_id>/reviews', methods=['POST', "DELETE"])
@jwt_required()
def review(product_id):
    if request.method == "POST":
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment')

        user_id = get_jwt()['sub']['id']
        vendor = Vendor.query.filter_by(id=user_id).first()

        if vendor:
            return make_response({"message": "Vendors cannot leave reviews!"}, 403)

        new_review = Review(rating=rating, comment=comment, product_id=product_id, buyer_id=user_id)
        db.session.add(new_review)
        db.session.commit()
        return make_response({"message": "Review created successfully!"}, 201)
    
    elif request.method == 'PATCH':
        review_id = request.args.get('review_id')
        review = Review.query.filter_by(id=review_id, buyer_id=user_id).first()

        if not review:
            return make_response({"message": "Review not found or not authorized to update!"}, 404)

        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment')

        if rating is not None:
            review.rating = rating
        if comment is not None:
            review.comment = comment

        db.session.commit()
        return make_response({"message": "Review updated successfully!"}, 200)


    elif request.method == 'DELETE':
        review_id = request.args.get('review_id')
        
        review = Review.query.filter_by(id=review_id, buyer_id=user_id).first()

        if not review:
            return make_response({"message": "Review not found or not authorized to delete!"}, 404)

        db.session.delete(review)
        db.session.commit()
        return make_response({"message": "Review deleted successfully!"}, 200)




#Home route or root page
@app.route("/")
def home():
    return make_response({"message" : "Welcome To this API generation"})


if __name__ == "__main__":
    app.run(port=8083, debug=True)