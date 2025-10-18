const username = "User"; // demo username

// Fetch and display products
async function fetchProducts() {
    const res = await fetch("/products");
    const data = await res.json();
    const list = document.getElementById("product-list");
    list.innerHTML = "";

    for (let id in data) {
        const p = data[id];
        const div = document.createElement("div");
        div.className = "product";
        div.innerHTML = `
            <img src="/static/images/${p.image}" alt="${p.name}" width="100">
            <h3>${p.name}</h3>
            <p>Rs. ${p.price} | Stock: ${p.stock}</p>
            <p>${p.description}</p>
            <button onclick="addToCart(${id})">Add to Cart</button>
            <button onclick="deleteProduct(${id})" style="background:#e53935;">Delete</button>
        `;
        list.appendChild(div);
    }
}

// Add product (with image)
const form = document.getElementById("product-form");
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const res = await fetch("/add_product", { method: "POST", body: formData });
    const data = await res.json();
    alert(data.message);
    form.reset();
    fetchProducts();
});

// Delete product
async function deleteProduct(id) {
    const res = await fetch(`/delete_product/${id}`, { method: "DELETE" });
    const data = await res.json();
    alert(data.message);
    fetchProducts();
}

// Add to cart
async function addToCart(id) {
    const item = { product_id: id, quantity: 1 };
    const res = await fetch(`/add_to_cart/${username}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item)
    });
    const data = await res.json();
    alert(data.message);
}

// View cart
async function viewCart() {
    const res = await fetch(`/view_cart/${username}`);
    const data = await res.json();
    const cartDiv = document.getElementById("cart-items");
    cartDiv.innerHTML = "";

    if (data.message) {
        cartDiv.innerHTML = "<p>Cart is empty.</p>";
        return;
    }

    data.forEach(item => {
        cartDiv.innerHTML += `🛍️ Product ID: ${item.product_id} | Quantity: ${item.quantity} <br>`;
    });
}

// Checkout
async function checkout() {
    const customer_name = document.getElementById("customer_name").value;
    const phone = document.getElementById("phone").value;

    if (!customer_name || !phone) {
        alert("Please enter your Name and Phone Number!");
        return;
    }

    const formData = new FormData();
    formData.append("customer_name", customer_name);
    formData.append("phone", phone);

    try {
        const res = await fetch(`/checkout/${username}`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        alert(data.message || data.detail || "Unknown response");
        fetchProducts(); // update stock
    } catch (err) {
        alert("Server error!");
        console.error(err);
    }
}

// Initial load
window.onload = fetchProducts;


