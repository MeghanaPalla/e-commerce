from datetime import datetime, timezone, timedelta
from app import app, db


@app.cli.command('seed')
def seed():
    """Create indexes and add sample products."""
    db.users.create_index('username', unique=True)
    db.users.create_index('email', unique=True)
    db.carts.create_index('user_id', unique=True)
    db.orders.create_index('user_id')
    db.products.create_index('category')

    if db.products.count_documents({}) > 0:
        print('Products already exist, skipping.')
        return

    items = [
        ('Steel Water Bottle', 'Insulated, keeps drinks cold for 24 hours.', 'Kitchen', 59900, 40),
        ('Ceramic Mug', 'Hand finished 300ml mug.', 'Kitchen', 29900, 50),
        ('Chopping Board', 'Solid bamboo board, easy to clean.', 'Kitchen', 44900, 22),
        ('Cotton T-Shirt', 'Plain round neck tee, 100% cotton.', 'Clothing', 39900, 100),
        ('Hoodie', 'Fleece lined pullover hoodie.', 'Clothing', 119900, 30),
        ('Wireless Mouse', 'Compact mouse with a quiet click.', 'Electronics', 69900, 25),
        ('Earphones', 'In-ear earphones with a built in mic.', 'Electronics', 79900, 30),
        ('Phone Stand', 'Foldable aluminium stand.', 'Electronics', 34900, 35),
        ('Desk Lamp', 'LED lamp with adjustable brightness.', 'Home', 129900, 15),
        ('Wall Clock', 'Silent sweep wall clock, 30cm.', 'Home', 49900, 18),
        ('Notebook (Pack of 3)', 'A5 ruled notebooks, 120 pages each.', 'Stationery', 24900, 60),
        ('Gel Pens (Set of 10)', 'Smooth writing gel pens in assorted colours.', 'Stationery', 19900, 80),
        ('Backpack', '20L daily backpack with a laptop sleeve.', 'Bags', 149900, 20),
        ('Tote Bag', 'Sturdy canvas tote with inner pocket.', 'Bags', 34900, 45),
        ('Yoga Mat', '6mm non slip mat.', 'Fitness', 89900, 18),
        ('Skipping Rope', 'Adjustable speed rope with ball bearings.', 'Fitness', 19900, 55),
    ]
    now = datetime.now(timezone.utc)
    docs = []
    for i, (name, desc, category, price, stock) in enumerate(items):
        docs.append({'name': name, 'description': desc, 'category': category,
                     'price_cents': price, 'stock': stock,
                     'created': now - timedelta(minutes=i)})
    db.products.insert_many(docs)
    print('Added {} products.'.format(len(docs)))
