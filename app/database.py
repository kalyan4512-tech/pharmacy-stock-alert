import os
import sqlite3
from datetime import datetime, date, timedelta

DB_DIR = os.environ.get("DB_DIR", os.path.join(os.path.dirname(__file__), "data"))
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(DB_DIR, "pharmacy.db"))

def get_db_connection():
    """Create a thread-safe connection to the SQLite database."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(seed=True):
    """Initialize database schema and seed initial data if empty."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        batch_number TEXT NOT NULL UNIQUE,
        manufacturer TEXT NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 0,
        min_threshold INTEGER NOT NULL DEFAULT 10,
        purchase_price REAL NOT NULL DEFAULT 0.0,
        selling_price REAL NOT NULL DEFAULT 0.0,
        mfg_date TEXT NOT NULL,
        expiry_date TEXT NOT NULL,
        supplier TEXT NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("SELECT COUNT(*) FROM medicines")
    count = cursor.fetchone()[0]

    if count == 0 and seed:
        today = date.today()
        # Seed realistic pharmacy records with dynamic dates so statuses are genuinely active
        seed_medicines = [
            # Expired medicines
            (
                "Amoxicillin 500mg",
                "Antibiotics",
                "AMX-2024-001",
                "Cipla Ltd",
                25,
                30,
                45.0,
                65.0,
                (today - timedelta(days=730)).strftime("%Y-%m-%d"),
                (today - timedelta(days=15)).strftime("%Y-%m-%d"), # Expired 15 days ago
                "Apex Pharma Distributors",
                "Broad-spectrum penicillin antibiotic for bacterial infections."
            ),
            (
                "Cough Syrup Dextro",
                "Respiratory",
                "CSD-2024-089",
                "Sun Pharma",
                4,
                15,
                55.0,
                85.0,
                (today - timedelta(days=365)).strftime("%Y-%m-%d"),
                (today - timedelta(days=5)).strftime("%Y-%m-%d"), # Expired 5 days ago
                "Metro Meds Supply",
                "Dry cough suppressant syrup 100ml."
            ),
            # Expiring Today
            (
                "Eye Drops Refresh",
                "Ophthalmic",
                "EDR-2025-112",
                "Allergan",
                8,
                10,
                120.0,
                160.0,
                (today - timedelta(days=180)).strftime("%Y-%m-%d"),
                today.strftime("%Y-%m-%d"), # Expiring Today
                "Vision Care Direct",
                "Lubricating eye drops for dry eyes."
            ),
            # Expiring Soon (Within 30 days)
            (
                "Cetirizine 10mg",
                "Antihistamines",
                "CTZ-2025-442",
                "Dr. Reddy's",
                12,
                20,
                18.0,
                30.0,
                (today - timedelta(days=360)).strftime("%Y-%m-%d"),
                (today + timedelta(days=7)).strftime("%Y-%m-%d"), # 7 days remaining
                "Apex Pharma Distributors",
                "Relief from allergy symptoms, hay fever, and hives."
            ),
            (
                "Azithromycin 250mg",
                "Antibiotics",
                "AZM-2025-301",
                "Zydus Healthcare",
                35,
                15,
                70.0,
                110.0,
                (today - timedelta(days=300)).strftime("%Y-%m-%d"),
                (today + timedelta(days=18)).strftime("%Y-%m-%d"), # 18 days remaining
                "National Medical Supplies",
                "Macrolide antibiotic used for respiratory tract infections."
            ),
            # Low Stock (quantity <= min_threshold)
            (
                "Metformin 500mg",
                "Antidiabetic",
                "MET-2026-805",
                "Lupin Ltd",
                8,
                25, # Low Stock: 8 <= 25
                22.0,
                38.0,
                (today - timedelta(days=90)).strftime("%Y-%m-%d"),
                (today + timedelta(days=400)).strftime("%Y-%m-%d"),
                "Apollo Logistics",
                "First-line medication for the treatment of type 2 diabetes."
            ),
            (
                "Omeprazole 20mg",
                "Gastrointestinal",
                "OMP-2026-991",
                "Torrent Pharma",
                5,
                20, # Low Stock: 5 <= 20
                35.0,
                55.0,
                (today - timedelta(days=60)).strftime("%Y-%m-%d"),
                (today + timedelta(days=360)).strftime("%Y-%m-%d"),
                "Metro Meds Supply",
                "Proton-pump inhibitor for acid reflux and GERD."
            ),
            # Out of Stock (quantity == 0)
            (
                "Ibuprofen 400mg",
                "Analgesics",
                "IBU-2026-050",
                "Abbott Healthcare",
                0,
                50, # Out of stock
                25.0,
                42.0,
                (today - timedelta(days=120)).strftime("%Y-%m-%d"),
                (today + timedelta(days=500)).strftime("%Y-%m-%d"),
                "Apollo Logistics",
                "Nonsteroidal anti-inflammatory drug (NSAID) for pain relief."
            ),
            # Normal Healthy Stock
            (
                "Paracetamol 650mg",
                "Analgesics & Antipyretic",
                "PCM-2026-554",
                "GlaxoSmithKline",
                450,
                100, # Normal: 450 > 100
                12.0,
                20.0,
                (today - timedelta(days=45)).strftime("%Y-%m-%d"),
                (today + timedelta(days=600)).strftime("%Y-%m-%d"),
                "Apex Pharma Distributors",
                "Fever reducer and mild-to-moderate pain reliever."
            ),
            (
                "Atorvastatin 10mg",
                "Cardiovascular",
                "ATV-2026-778",
                "Pfizer India",
                180,
                30,
                85.0,
                135.0,
                (today - timedelta(days=30)).strftime("%Y-%m-%d"),
                (today + timedelta(days=550)).strftime("%Y-%m-%d"),
                "National Medical Supplies",
                "Statin medication to prevent cardiovascular disease."
            ),
            (
                "Vitamin C & Zinc 500mg",
                "Vitamins & Supplements",
                "VCZ-2026-619",
                "Himalaya Wellness",
                220,
                40,
                40.0,
                70.0,
                (today - timedelta(days=20)).strftime("%Y-%m-%d"),
                (today + timedelta(days=480)).strftime("%Y-%m-%d"),
                "Herbal Care Direct",
                "Immunity support chewable tablets."
            ),
            (
                "Insulin Glargine 100IU",
                "Antidiabetic",
                "INS-2026-102",
                "Sanofi",
                60,
                15,
                450.0,
                620.0,
                (today - timedelta(days=15)).strftime("%Y-%m-%d"),
                (today + timedelta(days=250)).strftime("%Y-%m-%d"),
                "ColdChain Biologics",
                "Long-acting basal insulin analog for diabetes."
            )
        ]

        cursor.executemany("""
        INSERT INTO medicines (
            name, category, batch_number, manufacturer,
            quantity, min_threshold, purchase_price, selling_price,
            mfg_date, expiry_date, supplier, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_medicines)

    conn.commit()
    conn.close()

def get_all_medicines():
    """Retrieve all medicines ordered by id descending."""
    conn = get_db_connection()
    medicines = conn.execute("SELECT * FROM medicines ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(m) for m in medicines]

def get_medicine_by_id(medicine_id):
    """Retrieve single medicine by ID."""
    conn = get_db_connection()
    medicine = conn.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,)).fetchone()
    conn.close()
    return dict(medicine) if medicine else None

def add_medicine(data):
    """Add a new medicine record to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO medicines (
        name, category, batch_number, manufacturer,
        quantity, min_threshold, purchase_price, selling_price,
        mfg_date, expiry_date, supplier, description
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"].strip(),
        data["category"].strip(),
        data["batch_number"].strip(),
        data["manufacturer"].strip(),
        int(data["quantity"]),
        int(data["min_threshold"]),
        float(data["purchase_price"]),
        float(data["selling_price"]),
        data["mfg_date"].strip(),
        data["expiry_date"].strip(),
        data["supplier"].strip(),
        data.get("description", "").strip()
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def update_medicine(medicine_id, data):
    """Update existing medicine record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE medicines SET
        name = ?,
        category = ?,
        batch_number = ?,
        manufacturer = ?,
        quantity = ?,
        min_threshold = ?,
        purchase_price = ?,
        selling_price = ?,
        mfg_date = ?,
        expiry_date = ?,
        supplier = ?,
        description = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (
        data["name"].strip(),
        data["category"].strip(),
        data["batch_number"].strip(),
        data["manufacturer"].strip(),
        int(data["quantity"]),
        int(data["min_threshold"]),
        float(data["purchase_price"]),
        float(data["selling_price"]),
        data["mfg_date"].strip(),
        data["expiry_date"].strip(),
        data["supplier"].strip(),
        data.get("description", "").strip(),
        medicine_id
    ))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def delete_medicine(medicine_id):
    """Delete a medicine record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0

def get_categories():
    """Get distinct categories from database."""
    conn = get_db_connection()
    rows = conn.execute("SELECT DISTINCT category FROM medicines ORDER BY category").fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

