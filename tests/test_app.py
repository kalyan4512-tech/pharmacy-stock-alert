import pytest
import os
import sys
import tempfile

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from app import app
import database

@pytest.fixture
def client():
    # Use a temporary SQLite database for testing
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    database.DATABASE_PATH = db_path
    database.init_db(seed=True)

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.test_client() as client:
        yield client

    os.close(db_fd)
    if os.path.exists(db_path):
        os.remove(db_path)

def test_health_check_endpoint(client):
    """Test /health returns 200 and valid JSON."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "pharmacy-stock-alert"
    assert "database" in data
    assert data["database"]["status"] == "connected"

def test_dashboard_route(client):
    """Test dashboard loads with status 200 and expected titles."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Pharmacy Inventory Dashboard" in response.data
    assert b"Total Medicines" in response.data

def test_medicines_inventory_route(client):
    """Test /medicines page loads."""
    response = client.get("/medicines")
    assert response.status_code == 200
    assert b"Medicine Inventory Management" in response.data

def test_add_medicine_crud(client):
    """Test adding a new medicine."""
    new_med = {
        "name": "Dolo 650mg",
        "category": "Analgesics",
        "batch_number": "DOLO-TEST-999",
        "manufacturer": "Micro Labs",
        "quantity": "50",
        "min_threshold": "15",
        "purchase_price": "25.50",
        "selling_price": "35.00",
        "mfg_date": "2026-01-01",
        "expiry_date": "2027-12-31",
        "supplier": "Southern Pharma Hub",
        "description": "Popular antipyretic"
    }

    response = client.post("/medicines/add", data=new_med, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dolo 650mg" in response.data
    assert b"DOLO-TEST-999" in response.data

def test_edit_medicine_crud(client):
    """Test updating existing medicine."""
    # First get list to find an ID
    all_meds = database.get_all_medicines()
    med_id = all_meds[0]["id"]

    updated_data = {
        "name": "Updated Medicine Name",
        "category": all_meds[0]["category"],
        "batch_number": all_meds[0]["batch_number"],
        "manufacturer": all_meds[0]["manufacturer"],
        "quantity": "99",
        "min_threshold": "10",
        "purchase_price": "10.0",
        "selling_price": "15.0",
        "mfg_date": "2026-01-01",
        "expiry_date": "2028-01-01",
        "supplier": "Test Supplier",
        "description": "Updated description"
    }

    response = client.post(f"/medicines/edit/{med_id}", data=updated_data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Updated Medicine Name" in response.data

    fetched = database.get_medicine_by_id(med_id)
    assert fetched["name"] == "Updated Medicine Name"
    assert fetched["quantity"] == 99

def test_delete_medicine_crud(client):
    """Test deleting a medicine."""
    all_meds = database.get_all_medicines()
    initial_count = len(all_meds)
    med_id = all_meds[0]["id"]

    response = client.post(f"/medicines/delete/{med_id}", follow_redirects=True)
    assert response.status_code == 200

    after_meds = database.get_all_medicines()
    assert len(after_meds) == initial_count - 1
    assert database.get_medicine_by_id(med_id) is None

def test_alert_pages(client):
    """Test all alert endpoints."""
    res_center = client.get("/alerts")
    assert res_center.status_code == 200
    assert b"Centralized Alert Center" in res_center.data

    res_low = client.get("/alerts/low-stock")
    assert res_low.status_code == 200
    assert b"Low Stock Alerts" in res_low.data

    res_exp = client.get("/alerts/expiry")
    assert res_exp.status_code == 200
    assert b"Medicine Expiry Alerts" in res_exp.data

    res_expired = client.get("/alerts/expired")
    assert res_expired.status_code == 200
    assert b"Expired Medicines &amp; Quarantine Control" in res_expired.data or b"Expired Medicines & Quarantine Control" in res_expired.data

def test_reports_and_export(client):
    """Test reports and CSV export."""
    res_rep = client.get("/reports")
    assert res_rep.status_code == 200
    assert b"Pharmacy Financial &amp; Inventory Reports" in res_rep.data or b"Pharmacy Financial & Inventory Reports" in res_rep.data

    res_csv = client.get("/reports/export")
    assert res_csv.status_code == 200
    assert res_csv.headers["Content-Type"].startswith("text/csv")
    assert b"Medicine ID,Name,Category,Batch Number" in res_csv.data

def test_about_page(client):
    """Test about page."""
    response = client.get("/about")
    assert response.status_code == 200
    assert b"Pharmacy Medicine Stock Alert System" in response.data

def test_api_endpoints(client):
    """Test API JSON endpoints."""
    res_stats = client.get("/api/stats")
    assert res_stats.status_code == 200
    stats = res_stats.get_json()
    assert "total_medicines" in stats
    assert "total_stock" in stats
    assert "total_low_stock" in stats

    res_meds = client.get("/api/medicines")
    assert res_meds.status_code == 200
    meds = res_meds.get_json()
    assert isinstance(meds, list)
    assert len(meds) > 0

