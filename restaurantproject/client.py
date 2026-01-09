import requests

order = {
    "table": 2,
    "item": "Burger",
    "qty": 2
}

r = requests.post("http://127.0.0.1:5000/order", json=order)
print(r.json())
