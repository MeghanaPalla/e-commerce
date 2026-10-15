from app import app

@app.route("/")
def home():
    return "Welcome to our E-Commerce website!"


@app.route("/products")
def products():
    return "Here are all our products!"


@app.route("/cart")
def cart():
    return "your shopping cart"