from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
import threading

app = FastAPI(title="Online Cloth Store")

# Serve static files (Frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------
# DATABASE (in-memory)
# ---------------------------
products = {}
carts = {}
next_product_id = 1
lock = threading.Lock()  # To handle concurrency safely

# ---------------------------
# MODELS
# ---------------------------
class Product(BaseModel):
    name: str
    price: int
    stock: int
    description: str

class CartItem(BaseModel):
    product_id: int
    quantity: int


# ---------------------------
# FRONTEND ROUTE
# ---------------------------
@app.get("/", response_class=HTMLResponse)
def home_page():
    with open("static/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return html


# ---------------------------
# PRODUCT ROUTES
# ---------------------------
@app.get("/products")
def get_products():
    return products

@app.post("/add_product")
def add_product(product: Product):
    global next_product_id
    with lock:
        products[next_product_id] = product.dict()
        next_product_id += 1
    return {"message": "✅ Product added successfully!"}

@app.put("/update_stock/{product_id}")
def update_stock(product_id: int, product: Product):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    with lock:
        products[product_id] = product.dict()
    return {"message": "✅ Product updated successfully!"}

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    with lock:
        del products[product_id]
    return {"message": "🗑️ Product deleted successfully!"}


# ---------------------------
# CART ROUTES
# ---------------------------
@app.post("/add_to_cart/{username}")
def add_to_cart(username: str, item: CartItem):
    if item.product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    if username not in carts:
        carts[username] = []

    carts[username].append({"product_id": item.product_id, "quantity": item.quantity})
    return {"message": f"🛒 Item added to {username}'s cart."}

@app.get("/view_cart/{username}")
def view_cart(username: str):
    if username not in carts:
        raise HTTPException(status_code=404, detail="Cart not found for this user")
    return carts[username]


# ---------------------------
# CHECKOUT + PAYMENT (ASYNC)
# ---------------------------
async def simulate_payment(username: str):
    print(f"💳 Processing payment for {username}...")
    await asyncio.sleep(3)  # simulate 3s delay for payment gateway
    print(f"✅ Payment successful for {username}")
    print(f"📦 Order confirmed for {username}!\n")

@app.post("/checkout/{username}")
async def checkout(username: str):
    if username not in carts or not carts[username]:
        raise HTTPException(status_code=404, detail="Cart is empty")

    user_cart = carts[username]

    # Validate stock
    for item in user_cart:
        pid = item["product_id"]
        qty = item["quantity"]
        if products[pid]["stock"] < qty:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {products[pid]['name']}")

    # Deduct stock safely
    with lock:
        for item in user_cart:
            pid = item["product_id"]
            qty = item["quantity"]
            products[pid]["stock"] -= qty

    # Asynchronous payment simulation
    asyncio.create_task(simulate_payment(username))

    carts[username] = []
    return {"message": "💳 Payment processing... please wait for confirmation."}


