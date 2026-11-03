from flask import Flask

app = Flask(__name__)

medicines = [
    {"name": "Paracetamol", "quantity": 500, "expiry": "2027-05-15"},
    {"name": "Amoxicillin", "quantity": 20, "expiry": "2026-11-20"},
    {"name": "Cetirizine", "quantity": 100, "expiry": "2026-11-15"},
    {"name": "Ibuprofen", "quantity": 0, "expiry": "2027-06-10"},
]

@app.route("/")
def home():
    html = """
    <html>
    <head>
        <title>Pharmacy Stock Alert</title>
        <style>
            body {font-family:Arial;background:#eef2f7;padding:30px;}
            h1 {color:#123456;}
            table {width:100%;background:white;border-collapse:collapse;}
            th,td {padding:12px;border:1px solid #ddd;}
            th {background:#123456;color:white;}
            .alert {color:red;font-weight:bold;}
        </style>
    </head>
    <body>
    <h1>Pharmacy Medicine Stock Alert System</h1>
    <h3>Medicine Inventory Dashboard</h3>
    <table>
    <tr><th>Medicine</th><th>Quantity</th><th>Expiry</th><th>Status</th></tr>
    """

    for m in medicines:
        if m["quantity"] == 0:
            status = "Out of Stock"
        elif m["quantity"] < 50:
            status = "Low Stock"
        else:
            status = "In Stock"

        html += f"""
        <tr>
        <td>{m['name']}</td>
        <td>{m['quantity']}</td>
        <td>{m['expiry']}</td>
        <td class="alert">{status}</td>
        </tr>
        """

    html += "</table></body></html>"
    return html

@app.route("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
