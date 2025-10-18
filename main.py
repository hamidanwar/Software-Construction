from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import threading
import asyncio
import shutil
import os
import json

PRODUCTS_FILE = "products.json"

# Load products on startup
if os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, "r") as f:
        products = json.load(f)
        # Ensure keys are integers
        products = {int(k): v for k, v in products.items()}
        next_product_id = max(products.keys()) + 1 if products else 1
else:
    products = {}
    next_product_id = 1

# Function to save products
def save_products():
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(products, f)


app = FastAPI(title="Online Cloth Store")

# Serve frontend & images
app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory data
products = {}
carts = {}
next_product_id = 1
lock = threading.Lock()  # atomic stock updates

class CartItem(BaseModel):
    product_id: int
    quantity: int

# ---------------------------
# PRODUCT ROUTES
# ---------------------------

@app.get("/")
def home():
    return {"message": "Backend running successfully!"}

@app.get("/products")
def get_products():
    return products

@app.post("/add_product")
async def add_product(
    name: str = Form(...),
    price: int = Form(...),
    stock: int = Form(...),
    description: str = Form(...),
    image: UploadFile = File(...)
):
    global next_product_id
    ext = os.path.splitext(image.filename)[1]
    filename = f"{name.lower().replace(' ','')}{ext}"
    path = f"static/images/{filename}"

    # Save uploaded image
    with open(path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Atomic add
    with lock:
        products[next_product_id] = {
            "name": name,
            "price": price,
            "stock": stock,
            "description": description,
            "image": filename
        }
        next_product_id += 1

    return {"message": f"✅ Product '{name}' added successfully!"}

@app.delete("/delete_product/{pid}")
def delete_product(pid: int):
    if pid not in products:
        raise HTTPException(status_code=404, detail="Product not found")
    with lock:
        img_path = f"static/images/{products[pid]['image']}"
        if os.path.exists(img_path):
            os.remove(img_path)
        del products[pid]
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
    carts[username].append(item.dict())
    return {"message": f"🛒 Added to {username}'s cart"}

@app.get("/view_cart/{username}")
def view_cart(username: str):
    if username not in carts or not carts[username]:
        return {"message": "Cart empty"}
    return carts[username]

# ---------------------------
# CHECKOUT + PAYMENT
# ---------------------------

async def simulate_payment(username: str, customer_name: str, phone: str):
    print(f"💳 Processing payment for {customer_name} ({phone}) ... (simulated)")
    await asyncio.sleep(3)
    print(f"✅ Payment successful for {customer_name} ({phone})")
    print(f"📦 Order confirmed for {username}!\n")

@app.post("/checkout/{username}")
async def checkout(
    username: str, 
    customer_name: str = Form(...), 
    phone: str = Form(...)
):
    if username not in carts or not carts[username]:
        raise HTTPException(status_code=400, detail="Cart empty")

    with lock:
        for item in carts[username]:
            pid = item["product_id"]
            qty = item["quantity"]
            if products[pid]["stock"] < qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for {products[pid]['name']}"
                )
            products[pid]["stock"] -= qty

    asyncio.create_task(simulate_payment(username, customer_name, phone))
    carts[username] = []

    return {"message": f"Payment processing for {customer_name} ({phone})... you’ll receive confirmation soon!"}


