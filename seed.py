from app import app
from models import  *

with app.app_context():
    print("Populating the table")
    
    
    db.drop_all()
    db.create_all()
    
    

    print("Database has been seeded successfully!")
