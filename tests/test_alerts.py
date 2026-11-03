import pytest
from datetime import date, timedelta
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from alerts import get_stock_status, get_expiry_status, evaluate_medicine, calculate_dashboard_metrics

def test_stock_status_out_of_stock():
    """Quantity 0 must return OUT_OF_STOCK with danger badge."""
    res = get_stock_status(0, 10)
    assert res["code"] == "OUT_OF_STOCK"
    assert res["label"] == "OUT OF STOCK"
    assert res["badge_class"] == "bg-danger"
    assert res["is_alert"] is True

def test_stock_status_low_stock():
    """Quantity <= threshold (and > 0) must return LOW_STOCK."""
    res = get_stock_status(5, 10)
    assert res["code"] == "LOW_STOCK"
    assert res["label"] == "LOW STOCK"
    assert res["badge_class"] == "bg-danger"
    assert res["is_alert"] is True

    # Exactly at threshold
    res_exact = get_stock_status(10, 10)
    assert res_exact["code"] == "LOW_STOCK"
    assert res_exact["is_alert"] is True

def test_stock_status_normal():
    """Quantity > threshold must return NORMAL."""
    res = get_stock_status(50, 10)
    assert res["code"] == "NORMAL"
    assert res["label"] == "NORMAL"
    assert res["badge_class"] == "bg-success"
    assert res["is_alert"] is False

def test_expiry_status_expired():
    """Date before today must return EXPIRED."""
    today = date(2026, 11, 3)
    past_date = date(2026, 10, 20)
    res = get_expiry_status(past_date, current_date=today)
    assert res["code"] == "EXPIRED"
    assert res["label"] == "EXPIRED"
    assert res["badge_class"] == "bg-danger"
    assert res["row_class"] == "table-danger"
    assert res["is_alert"] is True

def test_expiry_status_expiring_today():
    """Date equal to today must return EXPIRING_TODAY."""
    today = date(2026, 11, 3)
    res = get_expiry_status(today, current_date=today)
    assert res["code"] == "EXPIRING_TODAY"
    assert res["label"] == "EXPIRING TODAY"
    assert res["badge_class"] == "bg-danger"
    assert res["is_alert"] is True

def test_expiry_status_expiring_soon():
    """Date within next 30 days must return EXPIRING_SOON."""
    today = date(2026, 11, 3)
    future_15_days = today + timedelta(days=15)
    res = get_expiry_status(future_15_days, current_date=today)
    assert res["code"] == "EXPIRING_SOON"
    assert res["label"] == "EXPIRING SOON"
    assert "bg-warning" in res["badge_class"]
    assert res["row_class"] == "table-warning"
    assert res["is_alert"] is True

    # Exactly 30 days away
    future_30_days = today + timedelta(days=30)
    res_30 = get_expiry_status(future_30_days, current_date=today)
    assert res_30["code"] == "EXPIRING_SOON"

def test_expiry_status_normal():
    """Date more than 30 days away must return NORMAL."""
    today = date(2026, 11, 3)
    future_60_days = today + timedelta(days=60)
    res = get_expiry_status(future_60_days, current_date=today)
    assert res["code"] == "NORMAL"
    assert res["label"] == "NORMAL"
    assert res["badge_class"] == "bg-success"
    assert res["is_alert"] is False

def test_evaluate_medicine_integration():
    """Test full medicine dictionary enrichment."""
    today = date(2026, 11, 3)
    raw_med = {
        "id": 1,
        "name": "Test Medicine",
        "category": "Antibiotics",
        "quantity": 5,
        "min_threshold": 10,
        "expiry_date": (today + timedelta(days=10)).strftime("%Y-%m-%d"),
        "purchase_price": 20.0,
        "selling_price": 30.0
    }
    evaluated = evaluate_medicine(raw_med, current_date=today)
    assert evaluated["stock_status"] == "LOW_STOCK"
    assert evaluated["expiry_status"] == "EXPIRING_SOON"
    assert evaluated["is_healthy"] is False

def test_dashboard_metrics_aggregation():
    """Test dynamic calculation of total stock, counts, and valuation."""
    today = date(2026, 11, 3)
    medicines = [
        {"id": 1, "quantity": 100, "min_threshold": 20, "purchase_price": 10.0, "selling_price": 15.0, "expiry_date": "2027-01-01"}, # Normal
        {"id": 2, "quantity": 5, "min_threshold": 10, "purchase_price": 20.0, "selling_price": 30.0, "expiry_date": "2027-01-01"},   # Low stock
        {"id": 3, "quantity": 0, "min_threshold": 10, "purchase_price": 5.0, "selling_price": 10.0, "expiry_date": "2027-01-01"},    # Out of stock
        {"id": 4, "quantity": 10, "min_threshold": 5, "purchase_price": 15.0, "selling_price": 25.0, "expiry_date": "2026-10-01"},   # Expired
        {"id": 5, "quantity": 20, "min_threshold": 5, "purchase_price": 12.0, "selling_price": 20.0, "expiry_date": "2026-11-20"},   # Expiring soon (17 days)
    ]
    metrics = calculate_dashboard_metrics(medicines, current_date=today)

    assert metrics["total_medicines"] == 5
    assert metrics["total_stock"] == 135
    assert metrics["low_stock_count"] == 1
    assert metrics["out_of_stock_count"] == 1
    assert metrics["total_low_stock"] == 2
    assert metrics["expired_count"] == 1
    assert metrics["expiring_soon_count"] == 1
    assert metrics["normal_medicines"] == 1
    # Valuation: 100*10 + 5*20 + 0*5 + 10*15 + 20*12 = 1000 + 100 + 0 + 150 + 240 = 1490.0
    assert metrics["total_valuation"] == 1490.0

