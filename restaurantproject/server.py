from flask import Flask, request, jsonify, session, redirect, url_for
import itertools
import json
import os
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key_change_this_in_production"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ORDERS_FILE = os.path.join(SCRIPT_DIR, "orders.json")
CREDENTIALS_FILE = os.path.join(SCRIPT_DIR, "credentials.json")

def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_credentials(creds):
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(creds, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, "r") as f:
            return json.load(f)
    return []

def save_orders():
    with open(ORDERS_FILE, "w") as f:
        json.dump(orders, f)

credentials = load_credentials()
orders = load_orders()
id_counter = itertools.count(max([o["id"] for o in orders] + [0]) + 1)

def require_login(f):
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        data = request.json
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        remember = data.get("remember", False)
        
        if username in credentials and credentials[username] == hash_password(password):
            session.permanent = remember
            session['username'] = username
            return jsonify({"status": "ok"})
        return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    
    return """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Login - Kitchen Orders</title>
<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
}
.container {
    background: white;
    padding: 48px;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    width: 100%;
    max-width: 420px;
    animation: slideIn 0.5s ease;
}
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.header {
    text-align: center;
    margin-bottom: 36px;
}
.logo {
    font-size: 3.5em;
    margin-bottom: 12px;
}
h1 {
    color: #333;
    font-size: 1.8em;
    font-weight: 700;
    margin-bottom: 8px;
}
.subtitle {
    color: #999;
    font-size: 0.95em;
}
.form-group {
    margin-bottom: 20px;
}
label {
    display: block;
    color: #555;
    font-weight: 600;
    font-size: 0.9em;
    margin-bottom: 8px;
}
input[type="text"], input[type="password"] {
    width: 100%;
    padding: 14px 16px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    font-size: 1em;
    transition: all 0.2s ease;
    font-family: inherit;
}
input[type="text"]:focus, input[type="password"]:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}
.remember-me {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 28px;
    margin-top: 12px;
}
.checkbox-wrapper {
    display: flex;
    align-items: center;
}
input[type="checkbox"] {
    appearance: none;
    width: 20px;
    height: 20px;
    border: 2px solid #e0e0e0;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
}
input[type="checkbox"]:hover {
    border-color: #667eea;
}
input[type="checkbox"]:checked {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-color: #667eea;
}
input[type="checkbox"]:checked::after {
    content: "✓";
    color: white;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    font-weight: bold;
}
.remember-label {
    color: #666;
    font-size: 0.9em;
    cursor: pointer;
}
button {
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1em;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}
button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}
button:disabled {
    opacity: 0.7;
}
.error {
    color: #ef476f;
    background: #fff5f5;
    padding: 12px;
    border-radius: 8px;
    margin-bottom: 20px;
    font-size: 0.9em;
    display: none;
    border-left: 4px solid #ef476f;
}
.error.show {
    display: block;
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <div class="logo">🍳</div>
        <h1>Kitchen Orders</h1>
        <p class="subtitle">Sign in to your account</p>
    </div>
    
    <form onsubmit="handleLogin(event)">
        <div class="error" id="error"></div>
        
        <div class="form-group">
            <label for="username">Username</label>
            <input type="text" id="username" placeholder="Enter your username" required>
        </div>
        
        <div class="form-group">
            <label for="password">Password</label>
            <input type="password" id="password" placeholder="Enter your password" required>
        </div>
        
        <div class="remember-me">
            <div class="checkbox-wrapper">
                <input type="checkbox" id="remember" name="remember">
            </div>
            <label for="remember" class="remember-label">Remember me for 30 days</label>
        </div>
        
        <button type="submit" id="loginBtn">Sign In</button>
    </form>
</div>

<script>
async function handleLogin(e) {
    e.preventDefault();
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const remember = document.getElementById("remember").checked;
    const errorDiv = document.getElementById("error");
    const loginBtn = document.getElementById("loginBtn");
    
    errorDiv.classList.remove("show");
    loginBtn.disabled = true;
    loginBtn.textContent = "Signing in...";
    
    try {
        const res = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password, remember })
        });
        
        const data = await res.json();
        
        if (res.ok) {
            window.location.href = "/";
        } else {
            errorDiv.textContent = data.message || "Invalid username or password";
            errorDiv.classList.add("show");
            loginBtn.disabled = false;
            loginBtn.textContent = "Sign In";
        }
    } catch (err) {
        errorDiv.textContent = "Connection error. Please try again.";
        errorDiv.classList.add("show");
        loginBtn.disabled = false;
        loginBtn.textContent = "Sign In";
    }
}
</script>
</body>
</html>
"""

@app.route("/")
def kitchen():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    return """
<!DOCTYPE html>
<html>
<head>
<title>Kitchen Display</title>
<style>
body {
    font-family: system-ui, sans-serif;
    background: linear-gradient(135deg, #0f1724, #071028);
    color: #e6eef8;
    padding: 28px;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 100vh;
}
.header-bar {
    width: 100%;
    max-width: 1200px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 22px;
}
.logout-btn {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    color: #e6eef8;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    transition: all 0.2s ease;
}
.logout-btn:hover {
    background: rgba(255,255,255,0.2);
}
h1 {
    text-align: center;
    color: #ffd166;
    margin-bottom: 22px;
    letter-spacing: 0.4px;
}
.tables-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    width: 100%;
    max-width: 1200px;
}
.table {
    background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
    border-radius: 12px;
    padding: 14px;
    box-shadow: 0 6px 18px rgba(2,6,23,0.6);
    border-left: 6px solid #06d6a0;
}
.table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.table-header h2 {
    margin: 0;
    font-size: 1.05em;
    flex: 1;
    cursor: pointer;
}
.table-checkbox {
    display: flex;
    align-items: center;
    gap: 8px;
}
.table-checkbox input[type="checkbox"] {
    appearance: none;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    border: 2px solid rgba(230,238,248,0.3);
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.04));
    cursor: pointer;
}
.table-checkbox input[type="checkbox"]:checked {
    background: linear-gradient(180deg, #ef476f, #ef476f);
    border-color: #ef476f;
}
.items-container {
    max-height: 500px;
    overflow-y: auto;
}
.order {
    background: rgba(255,255,255,0.02);
    padding: 10px;
    border-radius: 8px;
    margin: 8px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.left {
    display: flex;
    flex-direction: column;
}
.item {
    font-weight: 600;
    font-size: 1.02em;
}
.meta {
    font-size: 0.85em;
    color: rgba(230,238,248,0.7);
}
.tick {
    display: flex;
    align-items: center;
}
.tick input[type="checkbox"] {
    appearance: none;
    width: 22px;
    height: 22px;
    border-radius: 6px;
    border: 2px solid rgba(230,238,248,0.2);
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.04));
    cursor: pointer;
}
.tick input[type="checkbox"]:checked {
    background: linear-gradient(180deg, #06d6a0, #06b686);
    border-color: #06d6a0;
}
.order.completed {
    opacity: 0.5;
}
.order.completed .item {
    text-decoration: line-through;
    color: rgba(230,238,248,0.5);
}
.order-expandable {
    cursor: pointer;
    user-select: none;
}
.order-history {
    margin-top: 8px;
    padding: 8px;
    background: rgba(0,0,0,0.2);
    border-radius: 6px;
    font-size: 0.8em;
    color: rgba(230,238,248,0.6);
    display: none;
}
.order-history.show {
    display: block;
}
.order-history-item {
    margin: 4px 0;
}
.history-indicator {
    font-size: 1.1em;
    opacity: 0.6;
    margin-left: 6px;
    transition: opacity 0.2s ease;
}
.empty {
    text-align: center;
    opacity: 0.7;
}
</style>
</head>

<body>
<div class="header-bar">
    <h1>🍳 Kitchen Orders</h1>
    <button class="logout-btn" onclick="logout()">Logout</button>
</div>
<div id="tables" class="tables-grid"></div>

<script>
let expandedItems = new Set(JSON.parse(localStorage.getItem('expandedItems') || '[]'));

async function loadOrders() {
    const res = await fetch("/orders");
    const orders = await res.json();
    const container = document.getElementById("tables");
    container.innerHTML = "";

    if (orders.length === 0) {
        container.innerHTML = "<p class='empty'>No orders yet 🍃</p>";
        return;
    }

    const grouped = {};
    const tableFirstTime = {};
    
    for (const o of orders) {
        if (!grouped[o.table]) grouped[o.table] = [];
        grouped[o.table].push(o);
        if (!tableFirstTime[o.table]) tableFirstTime[o.table] = o.timestamp;
    }

    // Sort tables by first order time
    const sortedTables = Object.keys(grouped).sort((a, b) => 
        new Date(tableFirstTime[a]) - new Date(tableFirstTime[b])
    );

    const colors = ["#06d6a0", "#ffd166", "#ef476f", "#118ab2"];
    let i = 0;

    for (const table of sortedTables) {
        const div = document.createElement("div");
        div.className = "table";
        div.style.borderLeft = "6px solid " + colors[i++ % colors.length];
        
        const allCompleted = grouped[table].every(o => o.completed);
        
        const header = document.createElement("div");
        header.className = "table-header";
        header.innerHTML = `
            <h2>Table ${table}</h2>
            <div class="table-checkbox">
                <label class="tick">
                    <input type="checkbox" ${allCompleted ? 'checked' : ''} onchange="completeTable('${table}', this.checked)">
                </label>
            </div>
        `;
        div.appendChild(header);

        const itemsContainer = document.createElement("div");
        itemsContainer.className = "items-container";

        for (const o of grouped[table]) {
            const time = new Date(o.timestamp).toLocaleTimeString();
            const row = document.createElement("div");
            row.className = "order" + (o.completed ? " completed" : "");
            
            let historyHtml = "";
            const hasHistory = o.history && o.history.length > 1;
            if (hasHistory) {
                const isExpanded = expandedItems.has(String(o.id));
                historyHtml = `<div class="order-history ${isExpanded ? 'show' : ''}" id="history-${o.id}">`;
                for (let i = 0; i < o.history.length; i++) {
                    const h = o.history[i];
                    const hTime = new Date(h.timestamp).toLocaleTimeString();
                    historyHtml += `<div class="order-history-item">+${h.qty} @ ${hTime}</div>`;
                }
                historyHtml += `</div>`;
            }
            
            row.innerHTML = `
                <div class="left">
                    <div class="item" onclick="toggleHistory('${o.id}')" style="cursor: ${hasHistory ? 'pointer' : 'default'}; font-weight: 600;">${o.item}${hasHistory ? `<span class="history-indicator" id="indicator-${o.id}">${expandedItems.has(String(o.id)) ? '−' : '+'}</span>` : ''}</div>
                    <div class="meta">Qty ${o.qty} • ${time}</div>
                    ${historyHtml}
                </div>
                <label class="tick">
                    <input type="checkbox" ${o.completed ? 'checked' : ''} onchange="toggleDone(${o.id})">
                </label>
            `;
            itemsContainer.appendChild(row);
        }
        div.appendChild(itemsContainer);
        container.appendChild(div);
    }
}

function toggleHistory(id) {
    const historyEl = document.getElementById(`history-${id}`);
    const indicator = document.getElementById(`indicator-${id}`);
    if (historyEl) {
        historyEl.classList.toggle("show");
        const idStr = String(id);
        if (historyEl.classList.contains("show")) {
            expandedItems.add(idStr);
            if (indicator) indicator.textContent = '−';
        } else {
            expandedItems.delete(idStr);
            if (indicator) indicator.textContent = '+';
        }
        localStorage.setItem('expandedItems', JSON.stringify(Array.from(expandedItems)));
    }
}

async function toggleDone(id) {
    try {
        await fetch(`/done/${id}`, { method: "POST" });
    } catch (e) {
        console.error('Failed to toggle done', e);
    }
    loadOrders();
}

async function logout() {
    await fetch("/logout", { method: "POST" });
    window.location.href = "/login";
}

async function completeTable(table, isChecked) {
    try {
        if (isChecked) {
            await fetch(`/clear-table/${table}`, { method: "POST" });
        }
    } catch (e) {
        console.error('Failed to clear table', e);
    }
    loadOrders();
}

setInterval(loadOrders, 1000);
loadOrders();
</script>
</body>
</html>
"""


@app.route("/order")
def order_page():
    if 'username' not in session:
        return redirect(url_for('login_page'))
    
    return """
<!DOCTYPE html>
<html>
<head>
<title>New Order</title>
<style>
body {
    font-family: system-ui, sans-serif;
    background: linear-gradient(135deg, #ff9a76, #ff6f91);
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}
form {
    background: white;
    padding: 40px;
    width: 100%;
    max-width: 360px;
    border-radius: 18px;
    box-shadow: 0 25px 50px rgba(0,0,0,0.2);
}
h1 {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 0 0 24px 0;
    font-size: 1.5em;
    color: #333;
}
label {
    font-size: 0.9em;
    color: #666;
    font-weight: 600;
    display: block;
    margin-bottom: 8px;
}
input[type="text"], input[type="number"] {
    width: 100%;
    padding: 12px 14px;
    margin-bottom: 18px;
    font-size: 1em;
    border: 2px solid #e8e8e8;
    border-radius: 8px;
    box-sizing: border-box;
    transition: all 0.2s ease;
    font-family: inherit;
    background: #fafafa;
}
input[type="text"]:focus, input[type="number"]:focus {
    outline: none;
    border-color: #06d6a0;
    background: white;
    box-shadow: 0 0 0 3px rgba(6, 214, 160, 0.1);
}
button {
    width: 100%;
    padding: 13px 16px;
    margin-top: 12px;
    font-size: 1em;
    background: #06d6a0;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    color: white;
}
button:hover:not(:disabled) {
    background: #05c490;
    transform: translateY(-1px);
}
button:disabled {
    opacity: 0.65;
}
</style>
</head>

<body>
<form onsubmit="sendOrder(); return false;">
    <h1>🧾 New Order</h1>

    <label>Table</label>
    <input id="table" type="text" value="1" required>

    <label>Item</label>
    <input id="item" type="text" placeholder="Item name" required>

    <label>Quantity</label>
    <input id="qty" type="number" value="1" min="1" required>

    <button id="btn">Send Order</button>
</form>

<script>
async function sendOrder() {
    const btn = document.getElementById("btn");
    btn.textContent = "Sending...";
    btn.disabled = true;

    await fetch("/order", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            table: table.value,
            item: item.value,
            qty: qty.value
        })
    });

    btn.textContent = "Sent ✓";
    setTimeout(() => {
        btn.textContent = "Send Order";
        btn.disabled = false;
    }, 1000);

    item.value = "";
    qty.value = 1;
}
</script>
</body>
</html>
"""


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"status": "ok"})


@app.route("/order", methods=["POST"])
def receive_order():
    if 'username' not in session:
        return jsonify({"status": "error"}), 401
    
    data = request.json
    data["table"] = str(data["table"])
    data["item"] = str(data["item"])
    data["qty"] = int(data["qty"])
    
    existing = next((o for o in orders if o["table"] == data["table"] and o["item"] == data["item"]), None)
    
    if existing:
        if "history" not in existing:
            existing["history"] = [{"qty": existing["qty"], "timestamp": existing["timestamp"]}]
        existing["history"].append({"qty": data["qty"], "timestamp": datetime.now().isoformat()})
        existing["qty"] += data["qty"]
        existing["timestamp"] = datetime.now().isoformat()
    else:
        data["id"] = next(id_counter)
        data["timestamp"] = datetime.now().isoformat()
        data["completed"] = False
        data["history"] = [{"qty": data["qty"], "timestamp": data["timestamp"]}]
        orders.append(data)
    
    print("Order processed:", data)
    save_orders()
    return jsonify({"status": "ok"})


@app.route("/orders")
def get_orders():
    if 'username' not in session:
        return jsonify({"status": "error"}), 401
    return jsonify(orders)


@app.route("/done/<int:order_id>", methods=["POST"])
def done(order_id):
    if 'username' not in session:
        return jsonify({"status": "error"}), 401
    
    global orders
    order = next((o for o in orders if o["id"] == order_id), None)
    if order:
        order["completed"] = not order.get("completed", False)
    save_orders()
    return jsonify({"status": "toggled"})


@app.route("/complete-table/<table>", methods=["POST"])
def complete_table(table):
    if 'username' not in session:
        return jsonify({"status": "error"}), 401
    
    global orders
    for o in orders:
        if o["table"] == table:
            o["completed"] = True
    save_orders()
    return jsonify({"status": "completed"})


@app.route("/clear-table/<table>", methods=["POST"])
def clear_table(table):
    if 'username' not in session:
        return jsonify({"status": "error"}), 401
    
    global orders
    orders = [o for o in orders if o["table"] != table]
    save_orders()
    return jsonify({"status": "cleared"})


if not credentials:
    credentials["admin"] = hash_password("password123")
    save_credentials(credentials)
    print("Initialized default user: admin / password123")


app.run(host="0.0.0.0", port=5000)
