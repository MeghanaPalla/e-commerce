# MiniShop

A full-stack e-commerce app: **React** frontend, **Flask** REST API, **MongoDB** database.
The backend is organised like the [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
(`app/` package, `config.py`, `shop.py` entry point), but exposes a JSON API instead of HTML pages.

## Features
- Register / login with hashed passwords and JWT tokens
- Product search, category filter, sorting and pagination
- Product detail pages with stock
- Per-user shopping cart (add, change quantity, remove) with live total
- Checkout, stock deduction, order history and order detail
- Input validation and JSON error responses

## Run it

You need Python 3.10+, Node 18+ and a MongoDB server
(local install, or a free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster).

**Backend**
```
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then edit MONGO_URI / SECRET_KEY if needed
flask seed                        # creates indexes and 16 sample products
flask run                         # http://127.0.0.1:5000
```

**Frontend** (in a second terminal)
```
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

Open http://localhost:5173. The Vite dev server forwards `/api` calls to Flask.

**Tests** (use an in-memory fake Mongo, no server needed)
```
cd backend
pip install -r requirements-dev.txt
pytest
```

## API

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | /api/auth/register | | `username, email, password` |
| POST | /api/auth/login | | `username` (or email), `password` |
| GET | /api/auth/me | yes | current user |
| GET | /api/products | | `q, category, sort, page, per_page` |
| GET | /api/products/<id> | | |
| GET | /api/categories | | |
| GET | /api/cart | yes | |
| POST | /api/cart | yes | `product_id, quantity` |
| PUT | /api/cart/<product_id> | yes | `quantity` (0 removes) |
| DELETE | /api/cart/<product_id> | yes | |
| POST | /api/orders | yes | `full_name, address` |
| GET | /api/orders | yes | |
| GET | /api/orders/<id> | yes | |

`sort` is one of `newest`, `price_asc`, `price_desc`, `name`.
Send the token as `Authorization: Bearer <token>`.

## Collections
`users`, `products`, `carts` (one document per user), `orders` (items are copied in at purchase time).
