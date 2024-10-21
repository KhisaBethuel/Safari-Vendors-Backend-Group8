from app import app
from models import  *

with app.app_context():
    print("Populating the table")
    
    
    db.drop_all()
    db.create_all()
    
    buyer1 = Buyer(username='john_doe', email='john@example.com', password='password123')
    buyer2 = Buyer(username='jane_doe', email='jane@example.com', password='securepass456')
    
    # Seed Vendors
    vendor1 = Vendor(username='vendor_one', email='vendor1@example.com', password='vendorpass1')
    vendor2 = Vendor(username='vendor_two', email='vendor2@example.com', password='vendorpass2')

    # Seed Products
    product1 = Product(name='Coffee Mug', category='Home & Kitchen', price=12.99, image_url='http://example.com/mug.jpg')
    product2 = Product(name='T-Shirt', category='Clothing', price=19.99, image_url='http://example.com/shirt.jpg')
    product3 = Product(name='Smartphone', category='Electronics', price=499.99, image_url='http://example.com/phone.jpg')
    
    # Assign products to vendors (many-to-many relationship)
    vendor1.products.extend([product1, product2])
    vendor2.products.append(product3)
    
    # Seed Cart
    cart1 = Cart(buyer=buyer1, products=[product1, product3])
    cart2 = Cart(buyer=buyer2, products=[product2])
    
    # Seed Orders
    order1 = Order(buyer=buyer1, vendor=vendor1, total_price=32.98, status='Completed')
    order2 = Order(buyer=buyer2, vendor=vendor2, total_price=499.99, status='Pending')

    # Seed Reviews
    review1 = Review(product=product1, vendor=vendor1, rating=5, comment="Great quality mug!")
    review2 = Review(product=product2, vendor=vendor1, rating=4, comment="Nice T-shirt!")
    review3 = Review(product=product3, vendor=vendor2, rating=3, comment="Phone is good, but a bit expensive.")

    # Add seeded data to the session
    db.session.add_all([buyer1, buyer2, vendor1, vendor2, product1, product2, product3, cart1, cart2, order1, order2, review1, review2, review3])

    # Commit the session to save everything to the database
    db.session.commit()
    
    

    print("Database has been seeded successfully!")
