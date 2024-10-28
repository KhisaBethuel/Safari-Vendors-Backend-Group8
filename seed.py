from app import app
from models import *

with app.app_context():
    print("Populating the table")


    db.drop_all()
    db.create_all()

    
    buyer1 = Buyer(username='alice_smith', email='alice@example.com', password='alicepass')
    buyer2 = Buyer(username='bob_johnson', email='bob@example.com', password='bobpass')
    buyer3 = Buyer(username='charlie_brown', email='charlie@example.com', password='charliepass')

    
    vendor1 = Vendor(username='Wainaina', email='wainaina@example.com', password='vendor1pass')
    vendor2 = Vendor(username='Happy Cow Farms', email='happycow@example.com', password='vendor2pass')
    vendor3 = Vendor(username='Green Orchard', email='greenorchard@example.com', password='vendor3pass')
    vendor4 = Vendor(username='Golden Loaf', email='goldenloaf@example.com', password='vendor4pass')
    vendor5 = Vendor(username='Farm Fresh', email='farmfresh@example.com', password='vendor5pass')
    vendor6 = Vendor(username='Mwiti', email='mwiti@example.com', password='vendor6pass')
    vendor7 = Vendor(username='Willy Pozee', email='willypozee@example.com', password='vendor7pass')
    vendor8 = Vendor(username='Kimani', email='kimani@example.com', password='vendor8pass')
    vendor9 = Vendor(username='Mogarn', email='mogarn@example.com', password='vendor9pass')

    
    product1 = Product(name='Tomatoes', category='Groceries', price=60, image_url='https://www.lifeisagarden.co.za/wp-content/uploads/2016/08/5B2A2465.jpg')
    product2 = Product(name='Milk', category='Dairy', price=350, image_url='https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8bWlsa3xlbnwwfHwwfHx8MA%3D%3D')
    product3 = Product(name='Apples', category='Fruits', price=200, image_url='https://plus.unsplash.com/premium_photo-1661322640130-f6a1e2c36653?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8QXBwbGV8ZW58MHx8MHx8fDA%3D')
    product4 = Product(name='Bread', category='Bakery', price=150, image_url='https://plus.unsplash.com/premium_photo-1675727579991-16042ead1ddf?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTd8fEJyZWFkfGVufDB8fDB8fHww')
    product5 = Product(name='Eggs', category='Dairy', price=250, image_url='https://images.unsplash.com/photo-1498654077810-12c21d4d6dc3?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Nnx8RWdnc3xlbnwwfHwwfHx8MA%3D%3D')
    product6 = Product(name='Rice', category='Grains', price=300, image_url='https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTh8fFJpY2V8ZW58MHx8MHx8fDA%3D')
    product7 = Product(name='Pasta', category='Grains', price=280, image_url='https://plus.unsplash.com/premium_photo-1664472619078-9db415ebef44?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8UGFzdGF8ZW58MHx8MHx8fDA%3D')
    product8 = Product(name='Chicken', category='Meat', price=800, image_url='https://images.unsplash.com/photo-1535275226173-7ee8b465f0c1?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Q2hpY2tlbnxlbnwwfHwwfHx8MA%3D%3D')
    product9 = Product(name='Smocha', category='Snack', price=1200, image_url='https://www.wingsforlifeworldrun.com/uploads/fit/960/699/teams/5P8bd5/headerd.1711578224.jpg')
    product10 = Product(name='Irish Potatoes', category='Potatoes', price=550, image_url='https://images.unsplash.com/photo-1508313880080-c4bef0730395?w=400&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OHx8cG90YXRvZXN8ZW58MHx8MHx8fDA%3D')
    product11 = Product(name='Beans', category='Cereal', price=400, image_url='https://plus.unsplash.com/premium_photo-1670135170974-5352088c8ade?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8YmVhbnN8ZW58MHx8MHx8fDA%3D')
    product12 = Product(name='Carrots', category='Vegetables', price=50, image_url='https://www.economist.com/cdn-cgi/image/width=1424,quality=80,format=auto/sites/default/files/20180929_BLP506.jpg')
    product13 = Product(name='Mwiko', category='Cutlery', price=90, image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShu_0lUntot1vDmo1ZlJFADGbT5awT2mWMg3-RKxQgq8jz0ddSrN2qu3PhEMj2jdLcW0c&usqp=CAU')


    vendor1.products.extend([product1, product10, product11])  
    vendor2.products.extend([product2, product5])               
    vendor3.products.extend([product3])                         
    vendor4.products.append(product4)                           
    vendor5.products.extend([product6, product8])              
    vendor6.products.append(product9)                           
    vendor7.products.append(product7)                           
    vendor8.products.append(product12)                         
    vendor9.products.append(product13)                          

    
    cart1 = Cart(buyer=buyer1, products=[product1, product2, product6])
    cart2 = Cart(buyer=buyer2, products=[product3, product4, product8])
    cart3 = Cart(buyer=buyer3, products=[product5, product9, product10])


    order1 = Order(buyer=buyer1, vendor=vendor1, total_price=410, status='Completed')
    order2 = Order(buyer=buyer2, vendor=vendor2, total_price=650, status='Pending')
    order3 = Order(buyer=buyer3, vendor=vendor5, total_price=1300, status='Completed')

    
    review1 = Review(product=product1, vendor=vendor1, rating=5, comment="Fresh and ripe tomatoes!")
    review2 = Review(product=product2, vendor=vendor2, rating=4, comment="Creamy and delicious milk.")
    review3 = Review(product=product3, vendor=vendor3, rating=5, comment="Best apples I've ever had!")
    review4 = Review(product=product4, vendor=vendor4, rating=3, comment="Bread was good but could be fresher.")
    review5 = Review(product=product5, vendor=vendor2, rating=4, comment="Eggs were fresh, happy with the purchase.")
    review6 = Review(product=product6, vendor=vendor5, rating=5, comment="Best rice I've ever tasted!")
    review7 = Review(product=product7, vendor=vendor7, rating=4, comment="Pasta was perfect for dinner.")
    review8 = Review(product=product8, vendor=vendor5, rating=5, comment="Chicken was juicy and well-cooked.")
    review9 = Review(product=product9, vendor=vendor6, rating=5, comment="The best snack for my evening tea!")
    review10 = Review(product=product10, vendor=vendor9, rating=4, comment="Irish potatoes were great!")
    
    
    db.session.add_all([buyer1, buyer2, buyer3])
    db.session.add_all([vendor1, vendor2, vendor3, vendor4, vendor5, vendor6, vendor7, vendor8, vendor9])
    db.session.add_all([product1, product2, product3, product4, product5, product6, product7, product8, product9, product10, product11, product12, product13])
    db.session.add_all([cart1, cart2, cart3])
    db.session.add_all([order1, order2, order3])
    db.session.add_all([review1, review2, review3, review4, review5, review6, review7, review8, review9, review10])

    db.session.commit()
    print("Data seeded successfully!")
