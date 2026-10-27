import sys
from db import users_collection

if len(sys.argv) != 2:
    sys.exit("Usage: python make_admin.py user@example.com")

result = users_collection.update_one(
    {"email": sys.argv[1].strip().lower()},
    {"$set": {"role": "admin"}},
)
print("Promoted to admin." if result.matched_count else "No user with that email.")