import os
import csv
import io
from datetime import datetime, date, timezone
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify, Response
)

from database import (
    init_db, get_all_medicines, get_medicine_by_id, add_medicine,
    update_medicine, delete_medicine, get_categories, DATABASE_PATH
)
from alerts import (
    evaluate_medicine, calculate_dashboard_metrics, filter_alerts, get_stock_status, get_expiry_status
)
from models import MedicineValidator

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "pharmacy-stock-alert-super-secret-key-2026")

# Initialize database on app startup
with app.app_context():
    init_db(seed=True)

@app.context_processor
def inject_global_data():
    """Inject current date and alert counts for navbar badge indicators."""
    today = date.today()
    try:
        raw_medicines = get_all_medicines()
        metrics = calculate_dashboard_metrics(raw_medicines, current_date=today)
    except Exception:
        metrics = {
            "total_medicines": 0,
            "total_stock": 0,
            "total_low_stock": 0,
            "total_expiry_alerts": 0,
            "expired_count": 0,
            "expiring_soon_count": 0,
            "normal_medicines": 0
        }
    return {
        "current_date": today.strftime("%B %d, %Y"),
        "today_iso": today.strftime("%Y-%m-%d"),
        "nav_metrics": metrics
    }

@app.route("/")
def dashboard():
    """Dashboard displaying real-time metrics, status breakdowns, and urgent alerts."""
    raw_medicines = get_all_medicines()
    metrics = calculate_dashboard_metrics(raw_medicines)
    
    # Extract urgent alert medicines (low stock, out of stock, expiring soon, expired)
    urgent_alerts = [m for m in metrics["evaluated_medicines"] if m["stock_alert"] or m["expiry_alert"]]
    
    return render_template(
        "dashboard.html",
        metrics=metrics,
        urgent_alerts=urgent_alerts[:8],
        recent_medicines=metrics["evaluated_medicines"][:8]
    )

@app.route("/medicines")
def medicines_list():
    """Medicine inventory page with search and filtering."""
    search_query = request.args.get("search", "").strip().lower()
    selected_category = request.args.get("category", "").strip()
    selected_stock = request.args.get("stock", "").strip()
    selected_expiry = request.args.get("expiry", "").strip()

    raw_medicines = get_all_medicines()
    evaluated = [evaluate_medicine(m) for m in raw_medicines]

    # Filter logic
    filtered = []
    for med in evaluated:
        if search_query:
            query_match = (
                search_query in med["name"].lower() or
                search_query in med["batch_number"].lower() or
                search_query in med["manufacturer"].lower() or
                search_query in med["supplier"].lower() or
                search_query in med["category"].lower()
            )
            if not query_match:
                continue

        if selected_category and med["category"] != selected_category:
            continue

        if selected_stock:
            if selected_stock == "LOW" and med["stock_status"] not in ["LOW_STOCK", "OUT_OF_STOCK"]:
                continue
            elif selected_stock == "OUT" and med["stock_status"] != "OUT_OF_STOCK":
                continue
            elif selected_stock == "NORMAL" and med["stock_status"] != "NORMAL":
                continue

        if selected_expiry:
            if selected_expiry == "EXPIRED" and med["expiry_status"] != "EXPIRED":
                continue
            elif selected_expiry == "EXPIRING_SOON" and med["expiry_status"] not in ["EXPIRING_SOON", "EXPIRING_TODAY"]:
                continue
            elif selected_expiry == "NORMAL" and med["expiry_status"] != "NORMAL":
                continue

        filtered.append(med)

    categories = get_categories()
    return render_template(
        "medicines.html",
        medicines=filtered,
        categories=categories,
        search_query=search_query,
        selected_category=selected_category,
        selected_stock=selected_stock,
        selected_expiry=selected_expiry,
        total_count=len(filtered)
    )

@app.route("/medicines/add", methods=["GET", "POST"])
def add_medicine_route():
    """Add a new medicine record with validation."""
    if request.method == "POST":
        data = {
            "name": request.form.get("name", ""),
            "category": request.form.get("category", ""),
            "batch_number": request.form.get("batch_number", ""),
            "manufacturer": request.form.get("manufacturer", ""),
            "quantity": request.form.get("quantity", 0),
            "min_threshold": request.form.get("min_threshold", 10),
            "purchase_price": request.form.get("purchase_price", 0.0),
            "selling_price": request.form.get("selling_price", 0.0),
            "mfg_date": request.form.get("mfg_date", ""),
            "expiry_date": request.form.get("expiry_date", ""),
            "supplier": request.form.get("supplier", ""),
            "description": request.form.get("description", "")
        }

        errors = MedicineValidator.validate(data)
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("add_medicine.html", form_data=data, categories=get_categories())

        try:
            new_id = add_medicine(data)
            flash(f"Medicine '{data['name']}' (Batch: {data['batch_number']}) added successfully!", "success")
            return redirect(url_for("medicines_list"))
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                flash(f"Error: Batch number '{data['batch_number']}' already exists in inventory.", "danger")
            else:
                flash(f"Failed to add medicine: {str(e)}", "danger")
            return render_template("add_medicine.html", form_data=data, categories=get_categories())

    return render_template("add_medicine.html", form_data={}, categories=get_categories())

@app.route("/medicines/edit/<int:medicine_id>", methods=["GET", "POST"])
def edit_medicine_route(medicine_id):
    """Edit existing medicine record."""
    med = get_medicine_by_id(medicine_id)
    if not med:
        flash("Medicine not found.", "warning")
        return redirect(url_for("medicines_list"))

    if request.method == "POST":
        data = {
            "name": request.form.get("name", ""),
            "category": request.form.get("category", ""),
            "batch_number": request.form.get("batch_number", ""),
            "manufacturer": request.form.get("manufacturer", ""),
            "quantity": request.form.get("quantity", 0),
            "min_threshold": request.form.get("min_threshold", 10),
            "purchase_price": request.form.get("purchase_price", 0.0),
            "selling_price": request.form.get("selling_price", 0.0),
            "mfg_date": request.form.get("mfg_date", ""),
            "expiry_date": request.form.get("expiry_date", ""),
            "supplier": request.form.get("supplier", ""),
            "description": request.form.get("description", "")
        }

        errors = MedicineValidator.validate(data)
        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template("edit_medicine.html", medicine=data, medicine_id=medicine_id, categories=get_categories())

        try:
            update_medicine(medicine_id, data)
            flash(f"Medicine '{data['name']}' updated successfully!", "success")
            return redirect(url_for("medicines_list"))
        except Exception as e:
            flash(f"Failed to update medicine: {str(e)}", "danger")
            return render_template("edit_medicine.html", medicine=data, medicine_id=medicine_id, categories=get_categories())

    return render_template("edit_medicine.html", medicine=med, medicine_id=medicine_id, categories=get_categories())

@app.route("/medicines/delete/<int:medicine_id>", methods=["POST"])
def delete_medicine_route(medicine_id):
    """Delete a medicine record."""
    med = get_medicine_by_id(medicine_id)
    if not med:
        flash("Medicine not found.", "warning")
    else:
        name = med["name"]
        delete_medicine(medicine_id)
        flash(f"Medicine '{name}' (ID: #{medicine_id}) has been removed from inventory.", "info")
    return redirect(request.referrer or url_for("medicines_list"))

@app.route("/alerts")
def alerts_center():
    """Centralized alerts dashboard showing all active warnings."""
    raw_medicines = get_all_medicines()
    metrics = calculate_dashboard_metrics(raw_medicines)
    
    low_stock_list = filter_alerts(raw_medicines, "low_stock")
    expiry_list = filter_alerts(raw_medicines, "expiring_soon")
    expired_list = filter_alerts(raw_medicines, "expired")

    return render_template(
        "alerts.html",
        metrics=metrics,
        low_stock_list=low_stock_list,
        expiry_list=expiry_list,
        expired_list=expired_list
    )

@app.route("/alerts/low-stock")
def low_stock_alerts_page():
    """Dedicated Low Stock and Out of Stock Alerts page."""
    raw_medicines = get_all_medicines()
    low_stock_list = filter_alerts(raw_medicines, "low_stock")
    return render_template(
        "low_stock.html",
        medicines=low_stock_list,
        total_count=len(low_stock_list)
    )

@app.route("/alerts/expiry")
def expiry_alerts_page():
    """Dedicated Expiring Soon and Expiring Today Alerts page."""
    raw_medicines = get_all_medicines()
    expiry_list = filter_alerts(raw_medicines, "expiring_soon")
    return render_template(
        "expiry_alerts.html",
        medicines=expiry_list,
        total_count=len(expiry_list)
    )

@app.route("/alerts/expired")
def expired_medicines_page():
    """Dedicated Expired Medicines Quarantine & Disposal page."""
    raw_medicines = get_all_medicines()
    expired_list = filter_alerts(raw_medicines, "expired")
    return render_template(
        "expired.html",
        medicines=expired_list,
        total_count=len(expired_list)
    )

@app.route("/reports")
def reports_page():
    """Analytics and financial reports page."""
    raw_medicines = get_all_medicines()
    metrics = calculate_dashboard_metrics(raw_medicines)

    # Category breakdown
    category_summary = {}
    for med in metrics["evaluated_medicines"]:
        cat = med.get("category", "General")
        qty = int(med.get("quantity", 0))
        val = qty * float(med.get("purchase_price", 0.0))
        if cat not in category_summary:
            category_summary[cat] = {"count": 0, "stock": 0, "valuation": 0.0}
        category_summary[cat]["count"] += 1
        category_summary[cat]["stock"] += qty
        category_summary[cat]["valuation"] += val

    return render_template(
        "reports.html",
        metrics=metrics,
        categories=category_summary
    )

@app.route("/reports/export")
def export_csv():
    """Export current pharmacy stock to CSV file."""
    raw_medicines = get_all_medicines()
    evaluated = [evaluate_medicine(m) for m in raw_medicines]

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Medicine ID", "Name", "Category", "Batch Number", "Manufacturer",
        "Quantity", "Min Threshold", "Purchase Price", "Selling Price",
        "Mfg Date", "Expiry Date", "Supplier", "Stock Status", "Expiry Status"
    ])

    for m in evaluated:
        writer.writerow([
            m["id"], m["name"], m["category"], m["batch_number"], m["manufacturer"],
            m["quantity"], m["min_threshold"], m["purchase_price"], m["selling_price"],
            m["mfg_date"], m["expiry_date"], m["supplier"], m["stock_status"], m["expiry_status"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=pharmacy_inventory_{date.today().strftime('%Y%m%d')}.csv"}
    )

@app.route("/about")
def about_page():
    """Professional project architecture, tech stack, and DevOps pipeline overview."""
    return render_template("about.html")

@app.route("/health")
def health_check():
    """Production health-check endpoint for load balancers and deployment verification."""
    try:
        raw_medicines = get_all_medicines()
        return jsonify({
            "status": "healthy",
            "service": "pharmacy-stock-alert",
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "status": "connected",
                "path": DATABASE_PATH,
                "total_medicines": len(raw_medicines)
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route("/api/stats")
def api_stats():
    """JSON API endpoint returning real-time inventory statistics."""
    raw_medicines = get_all_medicines()
    metrics = calculate_dashboard_metrics(raw_medicines)
    metrics_data = {k: v for k, v in metrics.items() if k != "evaluated_medicines"}
    return jsonify(metrics_data)

@app.route("/api/medicines")
def api_medicines():
    """JSON API endpoint returning all evaluated medicines."""
    raw_medicines = get_all_medicines()
    evaluated = [evaluate_medicine(m) for m in raw_medicines]
    return jsonify(evaluated)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
