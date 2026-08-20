from app import create_app
from app.models import db, Shop, Staff, Item, Sale
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, UTC
import random

app = create_app()

def seed_data():
    with app.app_context():
        db.create_all()
        
        # Check if already seeded
        if Shop.query.first():
            print("Database already seeded!")
            return

        print("Seeding database...")
        
        shop = Shop(name="Mama's Corner Store", owner_name="Mama")
        db.session.add(shop)
        db.session.commit()
        
        owner = Staff(
            shop_id=shop.shop_id,
            name="Mama",
            username="owner",
            password_hash=generate_password_hash("password"),
            role="owner"
        )
        attendant1 = Staff(
            shop_id=shop.shop_id,
            name="John Doe",
            username="attendant",
            password_hash=generate_password_hash("password"),
            role="attendant"
        )
        attendant2 = Staff(
            shop_id=shop.shop_id,
            name="Jane Smith",
            username="attendant2",
            password_hash=generate_password_hash("password"),
            role="attendant"
        )
        attendant3 = Staff(
            shop_id=shop.shop_id,
            name="Mike Johnson",
            username="attendant3",
            password_hash=generate_password_hash("password"),
            role="attendant"
        )
        db.session.add_all([owner, attendant1, attendant2, attendant3])
        db.session.commit()
        
        items_data = [
            {"name": "Rice (5kg)", "category": "Groceries", "unit_type": "bag", "cost": 4000, "sell": 4500, "stock": 20, "reorder": 5},
            {"name": "Bread", "category": "Groceries", "unit_type": "loaf", "cost": 400, "sell": 500, "stock": 3, "reorder": 5},
            {"name": "Milk (Powder)", "category": "Beverages", "unit_type": "tin", "cost": 1500, "sell": 1800, "stock": 10, "reorder": 3},
            {"name": "Soap", "category": "Household", "unit_type": "piece", "cost": 250, "sell": 300, "stock": 50, "reorder": 10},
            {"name": "Sugar", "category": "Groceries", "unit_type": "kg", "cost": 600, "sell": 750, "stock": 4, "reorder": 5},
            {"name": "Toothpaste", "category": "Personal Care", "unit_type": "tube", "cost": 450, "sell": 600, "stock": 25, "reorder": 8},
            {"name": "Shampoo", "category": "Personal Care", "unit_type": "bottle", "cost": 1200, "sell": 1600, "stock": 1, "reorder": 5},
            {"name": "Coffee", "category": "Beverages", "unit_type": "jar", "cost": 2200, "sell": 2800, "stock": 6, "reorder": 5},
            {"name": "Potato Chips", "category": "Snacks", "unit_type": "pack", "cost": 300, "sell": 450, "stock": 30, "reorder": 10},
            {"name": "Chocolate Bar", "category": "Snacks", "unit_type": "piece", "cost": 150, "sell": 250, "stock": 45, "reorder": 15},
            {"name": "Detergent", "category": "Household", "unit_type": "box", "cost": 800, "sell": 1000, "stock": 5, "reorder": 5},
            {"name": "Cooking Oil (1L)", "category": "Groceries", "unit_type": "bottle", "cost": 1800, "sell": 2100, "stock": 12, "reorder": 4}
        ]
        
        items = []
        for data in items_data:
            item = Item(
                shop_id=shop.shop_id,
                name=data["name"],
                category=data["category"],
                unit_type=data["unit_type"],
                cost_price=data["cost"],
                selling_price=data["sell"],
                quantity_in_stock=data["stock"],
                reorder_threshold=data["reorder"]
            )
            items.append(item)
            db.session.add(item)
        db.session.commit()
        
        # Add some sales unevenly
        staff_list = [owner, attendant1, attendant1, attendant1, attendant1, attendant2, attendant2] 
        # attendant3 has no sales
        now = datetime.now(UTC).replace(tzinfo=None)
        
        for _ in range(80):
            item = random.choice(items)
            qty = random.randint(1, 4)
            staff_member = random.choice(staff_list)
            
            past_price = float(item.selling_price)
            if random.random() > 0.8:
                past_price = past_price * 0.9
                
            sale = Sale(
                item_id=item.item_id,
                staff_id=staff_member.staff_id,
                quantity_sold=qty,
                price_at_sale=past_price,
                total_amount=past_price * qty,
                timestamp=now - timedelta(days=random.randint(0, 14), hours=random.randint(1, 12))
            )
            db.session.add(sale)
        
        db.session.commit()
        print("Database seeded successfully!")
        print("Login credentials:")
        print("Owner: username='owner', password='password'")
        print("Attendant 1: username='attendant', password='password'")
        print("Attendant 2: username='attendant2', password='password'")
        print("Attendant 3: username='attendant3', password='password'")

if __name__ == '__main__':
    seed_data()
