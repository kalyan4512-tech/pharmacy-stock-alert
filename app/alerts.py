from datetime import datetime, date, timedelta

def parse_date(date_str):
    """Safely parse YYYY-MM-DD date string to a date object."""
    if not date_str:
        return None
    try:
        if isinstance(date_str, date):
            return date_str
        return datetime.strptime(str(date_str).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def get_stock_status(quantity, min_threshold):
    """
    Determine stock status based on rules:
    - quantity == 0: OUT OF STOCK (Red)
    - quantity <= min_threshold: LOW STOCK (Red)
    - quantity > min_threshold: NORMAL (Green)
    """
    try:
        qty = int(quantity)
        threshold = int(min_threshold)
    except (ValueError, TypeError):
        qty = 0
        threshold = 10

    if qty == 0:
        return {
            "code": "OUT_OF_STOCK",
            "label": "OUT OF STOCK",
            "badge_class": "bg-danger",
            "alert_level": "critical",
            "is_alert": True
        }
    elif qty <= threshold:
        return {
            "code": "LOW_STOCK",
            "label": "LOW STOCK",
            "badge_class": "bg-danger",
            "alert_level": "warning",
            "is_alert": True
        }
    else:
        return {
            "code": "NORMAL",
            "label": "NORMAL",
            "badge_class": "bg-success",
            "alert_level": "normal",
            "is_alert": False
        }

def get_expiry_status(expiry_date_val, current_date=None):
    """
    Determine expiry status based on rules:
    1. expiry_date < today: EXPIRED (Red)
    2. expiry_date == today: EXPIRING TODAY (Red)
    3. expiry_date <= today + 30 days: EXPIRING SOON (Orange)
    4. expiry_date > today + 30 days: NORMAL (Green)
    """
    today = current_date if current_date else date.today()
    exp_date = parse_date(expiry_date_val)

    if not exp_date:
        return {
            "code": "UNKNOWN",
            "label": "UNKNOWN DATE",
            "badge_class": "bg-secondary",
            "row_class": "",
            "days_remaining": 0,
            "is_alert": False
        }

    days_diff = (exp_date - today).days

    if days_diff < 0:
        return {
            "code": "EXPIRED",
            "label": "EXPIRED",
            "badge_class": "bg-danger",
            "row_class": "table-danger",
            "days_remaining": days_diff,
            "is_alert": True,
            "message": f"Expired {abs(days_diff)} day(s) ago"
        }
    elif days_diff == 0:
        return {
            "code": "EXPIRING_TODAY",
            "label": "EXPIRING TODAY",
            "badge_class": "bg-danger",
            "row_class": "table-danger",
            "days_remaining": 0,
            "is_alert": True,
            "message": "Expires today"
        }
    elif days_diff <= 30:
        return {
            "code": "EXPIRING_SOON",
            "label": "EXPIRING SOON",
            "badge_class": "bg-warning text-dark",
            "row_class": "table-warning",
            "days_remaining": days_diff,
            "is_alert": True,
            "message": f"Expires in {days_diff} day(s)"
        }
    else:
        return {
            "code": "NORMAL",
            "label": "NORMAL",
            "badge_class": "bg-success",
            "row_class": "",
            "days_remaining": days_diff,
            "is_alert": False,
            "message": f"{days_diff} days remaining"
        }

def evaluate_medicine(medicine, current_date=None):
    """Evaluate a single medicine dictionary and add stock and expiry status metadata."""
    med = dict(medicine)
    stock_eval = get_stock_status(med.get("quantity", 0), med.get("min_threshold", 10))
    expiry_eval = get_expiry_status(med.get("expiry_date"), current_date=current_date)

    med["stock_status"] = stock_eval["code"]
    med["stock_label"] = stock_eval["label"]
    med["stock_badge"] = stock_eval["badge_class"]
    med["stock_alert"] = stock_eval["is_alert"]

    med["expiry_status"] = expiry_eval["code"]
    med["expiry_label"] = expiry_eval["label"]
    med["expiry_badge"] = expiry_eval["badge_class"]
    med["expiry_row_class"] = expiry_eval["row_class"]
    med["days_remaining"] = expiry_eval["days_remaining"]
    med["expiry_message"] = expiry_eval.get("message", "")
    med["expiry_alert"] = expiry_eval["is_alert"]

    # Overall Status: An expired medicine must never be marked normal
    med["is_expired_or_today"] = expiry_eval["code"] in ["EXPIRED", "EXPIRING_TODAY"]
    med["is_healthy"] = (stock_eval["code"] == "NORMAL") and (expiry_eval["code"] == "NORMAL")

    return med

def calculate_dashboard_metrics(medicines_list, current_date=None):
    """
    Calculate summary statistics across all medicines dynamically:
    - Total Medicines
    - Total Available Stock
    - Low Stock Medicines
    - Expired Medicines
    - Expiring Soon Medicines
    - Normal Medicines
    """
    today = current_date if current_date else date.today()

    total_medicines = len(medicines_list)
    total_stock = 0
    low_stock_count = 0
    out_of_stock_count = 0
    expired_count = 0
    expiring_today_count = 0
    expiring_soon_count = 0
    normal_medicines_count = 0
    total_valuation = 0.0
    potential_revenue = 0.0

    evaluated_medicines = []

    for raw_med in medicines_list:
        med = evaluate_medicine(raw_med, current_date=today)
        evaluated_medicines.append(med)

        qty = int(med.get("quantity", 0))
        purchase_price = float(med.get("purchase_price", 0.0))
        selling_price = float(med.get("selling_price", 0.0))

        total_stock += qty
        total_valuation += (qty * purchase_price)
        potential_revenue += (qty * selling_price)

        # Stock alert breakdown
        if med["stock_status"] == "OUT_OF_STOCK":
            out_of_stock_count += 1
        elif med["stock_status"] == "LOW_STOCK":
            low_stock_count += 1

        # Expiry alert breakdown
        if med["expiry_status"] == "EXPIRED":
            expired_count += 1
        elif med["expiry_status"] == "EXPIRING_TODAY":
            expiring_today_count += 1
        elif med["expiry_status"] == "EXPIRING_SOON":
            expiring_soon_count += 1

        # Normal medicines: Not low/out of stock and NOT expired/expiring soon
        if med["is_healthy"]:
            normal_medicines_count += 1

    return {
        "total_medicines": total_medicines,
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "total_low_stock": low_stock_count + out_of_stock_count,
        "expired_count": expired_count,
        "expiring_today_count": expiring_today_count,
        "expiring_soon_count": expiring_soon_count,
        "total_expiry_alerts": expired_count + expiring_today_count + expiring_soon_count,
        "normal_medicines": normal_medicines_count,
        "total_valuation": round(total_valuation, 2),
        "potential_revenue": round(potential_revenue, 2),
        "evaluated_medicines": evaluated_medicines
    }

def filter_alerts(medicines_list, alert_type, current_date=None):
    """Filter medicines by specific alert category."""
    today = current_date if current_date else date.today()
    results = []

    for raw_med in medicines_list:
        med = evaluate_medicine(raw_med, current_date=today)
        if alert_type == "low_stock":
            if med["stock_status"] in ["LOW_STOCK", "OUT_OF_STOCK"]:
                results.append(med)
        elif alert_type == "out_of_stock":
            if med["stock_status"] == "OUT_OF_STOCK":
                results.append(med)
        elif alert_type == "expired":
            if med["expiry_status"] == "EXPIRED":
                results.append(med)
        elif alert_type == "expiring_soon":
            if med["expiry_status"] in ["EXPIRING_SOON", "EXPIRING_TODAY"]:
                results.append(med)
        elif alert_type == "all_alerts":
            if med["stock_alert"] or med["expiry_alert"]:
                results.append(med)
    return results

