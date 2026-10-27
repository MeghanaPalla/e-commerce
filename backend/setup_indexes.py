from db import users_collection

users_collection.create_index("email", unique=True)
print("Unique index on users.email created")