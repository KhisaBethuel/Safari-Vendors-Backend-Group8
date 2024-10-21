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



#Home route or root page
@app.route("/")
def home():
    return "Welcome To this API generation"


if __name__ == "__main__":
    app.run(port=8083, debug=True)