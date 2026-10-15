import re
import pandas as pd
from pathlib import Path
from db import products_collection

csv_path = Path(__file__).parent / "data" / "amazon.csv"
df = pd.read_csv(csv_path)
print("Rows read:", len(df))

def to_number(series):
    cleaned = series.astype(str).str.replace(r"[₹,|%]", "", regex=True)
    return pd.to_numeric(cleaned, errors="coerce")

def pretty(text):
    # "Computers&Accessories" -> "Computers & Accessories"
    # "HomeTheater,TV&Video" -> "Home Theater, TV & Video"
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = text.replace("&", " & ").replace(",", ", ")
    return re.sub(r"\s+", " ", text).strip()

df["price"] = to_number(df["discounted_price"])
df["original_price"] = to_number(df["actual_price"])
df["discount"] = to_number(df["discount_percentage"])
df["rating_num"] = pd.to_numeric(df["rating"], errors="coerce")
df["rating_count_num"] = to_number(df["rating_count"])

df = df.dropna(subset=["product_name", "price"])
df = df.drop_duplicates(subset="product_id")
print("Unique valid products:", len(df))

def clean(value):
    return None if pd.isna(value) else value

products = []
for r in df.itertuples():
    parts = [pretty(c) for c in str(r.category).split("|")]
    products.append({
        "product_id": r.product_id,
        "name": r.product_name,
        "description": [b.strip() for b in str(r.about_product).split("|") if b.strip()],
        "price": float(r.price),
        "original_price": clean(r.original_price),
        "discount_percent": clean(r.discount),
        "category": parts[0],
        "subcategories": parts[1:],
        "rating": clean(r.rating_num),
        "rating_count": None if pd.isna(r.rating_count_num) else int(r.rating_count_num),
        "image": r.img_link,
        "stock": 20,
    })

products_collection.delete_many({})
products_collection.insert_many(products)
products_collection.create_index("name")
products_collection.create_index("category")
print(f"Inserted {len(products)} products")