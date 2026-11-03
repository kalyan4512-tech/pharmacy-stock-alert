# MedStock PRO — Pharmacy Medicine Stock Alert System with AWS & DevOps

[![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-Jenkins%20Automated-blue)](http://127.0.0.1:8080)
[![Cloud](https://img.shields.io/badge/Cloud-Amazon%20ECR%20%7C%20EC2%20%7C%20SSM-orange)](https://aws.amazon.com)
[![Platform](https://img.shields.io/badge/Platform-Docker%20Container-2496ED)](https://www.docker.com)
[![Python](https://img.shields.io/badge/Backend-Python%20%7C%20Flask-3776AB)](https://flask.palletsprojects.com)
[![Status](https://img.shields.io/badge/Deployment-Live%20200%20OK-success)](http://13.223.206.23:5001)

An enterprise-grade, full-stack pharmacy inventory management and automated alert system developed as a capstone project for **B.Tech Artificial Intelligence & Data Science**. 

This system solves critical pharmaceutical supply chain challenges: preventing stockouts of life-saving medicines, enforcing minimum inventory replenishment thresholds, dynamically tracking medicine expiry dates to prevent dispensing expired products, and managing quarantine disposal—backed by a production-ready **Zero-SSH CI/CD pipeline** leveraging Jenkins, Docker, Amazon ECR, and AWS Systems Manager (SSM) Run Command to Amazon EC2.

---

## 🌐 Live Application URLs

- **Live Application:** [http://13.223.206.23:5001](http://13.223.206.23:5001)
- **Health Check Endpoint:** [http://13.223.206.23:5001/health](http://13.223.206.23:5001/health)
- **Inventory Statistics API:** [http://13.223.206.23:5001/api/stats](http://13.223.206.23:5001/api/stats)
- **Medicines JSON API:** [http://13.223.206.23:5001/api/medicines](http://13.223.206.23:5001/api/medicines)

---

## 📑 Table of Contents

1. [Features & System Capabilities](#-features--system-capabilities)
2. [Alert Logic & Business Rules](#-alert-logic--business-rules)
3. [Technology Stack](#-technology-stack)
4. [Architecture & DevOps Pipeline](#-architecture--devops-pipeline)
5. [Project Structure](#-project-structure)
6. [Local Development & Installation](#-local-development--installation)
7. [Docker Instructions](#-docker-instructions)
8. [Jenkins CI/CD Automation](#-jenkins-cicd-automation)
9. [AWS Cloud Infrastructure (ECR, EC2, SSM)](#-aws-cloud-infrastructure-ecr-ec2-ssm)
10. [Automated Testing & QA](#-automated-testing--qa)

---

## ✨ Features & System Capabilities

### 1. Executive Pharmacy Dashboard
- **6 Real-Time Key Metric Cards:** Total Medicines, Total Stock Units, Low Stock / Depleted, Expired (Quarantined), Expiring Soon (30-day window), and Normal Healthy Stock.
- **Urgent Alert Feed:** Real-time stream of items requiring immediate pharmacist action.
- **Financial Valuation:** Real-time computation of inventory acquisition costs, projected sales revenue, and profit margins.

### 2. Comprehensive Medicine Management (Full CRUD)
- **Attributes Tracked:** Medicine Name, Category, Unique Batch Number, Manufacturer, Current Quantity, Minimum Stock Threshold, Purchase Price, Selling Price, Manufacturing Date, Expiry Date, Supplier Contact, and Detailed Storage Notes.
- **Search & Multi-Facet Filtering:** Fast search across names, batches, suppliers, and manufacturers, alongside Category, Stock Level, and Expiry Status filters.
- **Instant Validation:** Input validation for non-negative values, unique batch constraints, and chronological date logic (expiry date must follow manufacturing date).

### 3. Real-Time Alert Center
- **Low Stock Tracker:** Flags medications where stock has dropped to or below the minimum safety threshold, calculating unit deficits for restock orders.
- **Expiry Early Warning:** Proactive identification of medicines within a 30-day expiry window for prioritized dispensing or supplier returns.
- **Strict Expiry Quarantine:** Isolates expired medications, prevents them from being counted as healthy stock, and logs estimated financial write-offs with one-click disposal.

### 4. Auditing & Reporting
- Category-wise distribution and financial risk analysis.
- Instant **CSV Export** for warehouse inventory audits, destruction manifests, and supplier reordering.

---

## 🧠 Alert Logic & Business Rules

### A. Stock Alert Rules
| Condition | Status Code | UI Badge | Alert Level | Action Required |
|---|---|---|---|---|
| `Quantity == 0` | `OUT_OF_STOCK` | `bg-danger` (Red) | Critical | Immediate emergency restock |
| `0 < Quantity <= Min Threshold` | `LOW_STOCK` | `bg-danger` (Red) | Warning | Supplier purchase order |
| `Quantity > Min Threshold` | `NORMAL` | `bg-success` (Green) | Normal | Stock levels healthy |

### B. Expiry Tracking Rules (Dynamically Computed Against Current Date)
| Condition | Status Code | UI Badge | Row Highlight | Workflow Action |
|---|---|---|---|---|
| `Expiry Date < Today` | `EXPIRED` | `bg-danger` (Red) | `table-danger` | Immediate quarantine & disposal |
| `Expiry Date == Today` | `EXPIRING_TODAY` | `bg-danger` (Red) | `table-danger` | Urgent disposal / return |
| `Today < Expiry Date <= Today + 30 Days` | `EXPIRING_SOON` | `bg-warning text-dark` (Orange) | `table-warning` | Priority dispensing / return |
| `Expiry Date > Today + 30 Days` | `NORMAL` | `bg-success` (Green) | None | Shelf stable |

> **Critical Safety Constraint:** Any medicine classified as `EXPIRED` or `EXPIRING_TODAY` is strictly quarantined and excluded from the healthy stock metric.

---

## 🛠 Technology Stack

- **Backend:** Python 3.12 / 3.15, Flask 3.1.3, Gunicorn WSGI
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons
- **Database:** SQLite 3 with persistent Docker volume storage (`/app/data`)
- **Testing:** Pytest 9.2 (19 automated unit & integration tests)
- **Containerization:** Docker (multi-arch `linux/amd64` production builds)
- **CI/CD Orchestration:** Jenkins Declarative Pipeline (8 automated stages)
- **Container Registry:** Amazon Elastic Container Registry (Amazon ECR)
- **Cloud Compute:** Amazon EC2 (`i-090065bd6065310a0`, Amazon Linux 2)
- **Remote Configuration:** AWS Systems Manager (SSM) Run Command (**Zero SSH key dependency**)
- **Version Control:** Git & GitHub (`kalyan4512-tech/pharmacy-stock-alert`)

---

## 🏗 Architecture & DevOps Pipeline

```
┌──────────────┐       git push        ┌──────────────────┐
│   VS Code    │ ────────────────────> │  GitHub (main)   │
│ (Developer)  │                       └────────┬─────────┘
└──────────────┘                                │
                                         Webhook / Poll
                                                │
                                       ┌────────▼─────────┐
                                       │     Jenkins      │
                                       │  CI/CD Pipeline  │
                                       └────────┬─────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         │                                      │                                      │
   [Stage 2: Validate]                  [Stage 3: Build]                      [Stage 4 & 5: Push]
   • Python syntax check                • docker build                        • aws ecr get-login
   • Pytest 19/19 tests                 • --platform linux/amd64              • docker push ECR
         │                                      │                                      │
         └──────────────────────────────────────┼──────────────────────────────────────┘
                                                │
                                       ┌────────▼─────────┐
                                       │    Amazon ECR    │
                                       │ (Container Repo) │
                                       └────────┬─────────┘
                                                │
                                       [Stage 6: Deploy]
                                       aws ssm send-command
                                                │
                                       ┌────────▼─────────┐
                                       │  AWS SSM Agent   │
                                       └────────┬─────────┘
                                                │ Zero SSH
                                       ┌────────▼─────────┐
                                       │    Amazon EC2    │
                                       │  Docker Engine   │
                                       │  Container:5001  │
                                       │ Volume: /app/data│
                                       └────────┬─────────┘
                                                │
                                       [Stage 7: Verify]
                                       curl /health -> 200 OK
                                                │
                                       ┌────────▼─────────┐
                                       │ Live Pharmacy UI │
                                       │ http://<IP>:5001 │
                                       └──────────────────┘
```

---

## 📁 Project Structure

```
pharmacy-stock-alert/
├── .dockerignore                  # Docker build exclusion rules
├── .gitignore                     # Git tracking exclusions (secrets, pycache, db)
├── Dockerfile                     # Multi-stage production container specification
├── Jenkinsfile                    # Automated 8-stage declarative CI/CD pipeline
├── README.md                      # Comprehensive project documentation
├── app/
│   ├── Dockerfile                 # Context-specific Dockerfile for `./app` builds
│   ├── alerts.py                  # Stock threshold & 30-day expiry calculation logic
│   ├── app.py                     # Flask routes, REST APIs, and application lifecycle
│   ├── database.py                # SQLite schema, persistent storage, and CRUD ops
│   ├── models.py                  # Input validation and business constraint rules
│   ├── requirements.txt           # Python production dependencies
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css          # Medical navy & teal responsive UI styling
│   │   └── js/
│   │       └── app.js             # Client-side dynamic search and date validation
│   └── templates/
│       ├── about.html             # Project architecture and B.Tech AI & DS info
│       ├── add_medicine.html      # Medicine creation form with validation
│       ├── alerts.html            # Centralized Alert Center hub
│       ├── base.html              # Master layout with responsive navbar & badges
│       ├── dashboard.html         # Executive overview with 6 metric cards
│       ├── edit_medicine.html     # Medicine update and restock form
│       ├── expired.html           # Expired stock quarantine and destruction log
│       ├── expiry_alerts.html     # Imminent 30-day expiry tracking page
│       ├── low_stock.html         # Depleted and below-threshold restock list
│       ├── medicines.html         # Full inventory table with multi-facet filters
│       └── reports.html           # Financial valuation and category audit
├── deployment/
│   └── deploy.sh                  # Host deployment script for EC2 / SSM runner
└── tests/
    ├── test_alerts.py             # Unit tests for stock and expiry calculation rules
    └── test_app.py                # Integration tests for Flask routes, CRUD, and APIs
```

---

## 🚀 Local Development & Installation

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Setup Virtual Environment
```bash
# Clone the repository
git clone https://github.com/kalyan4512-tech/pharmacy-stock-alert.git
cd pharmacy-stock-alert

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r app/requirements.txt pytest
```

### 3. Run Unit Tests
```bash
pytest tests/ -v
```

### 4. Start Development Server
```bash
python app/app.py
```
Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🐳 Docker Instructions

### 1. Build the Docker Image
```bash
# Build from the app context
docker build -t pharmacy-stock-alert ./app

# Or build for AWS amd64 architecture:
docker build --platform linux/amd64 -t pharmacy-stock-alert ./app
```

### 2. Run the Container Locally with Persistent Storage
```bash
docker run -d \
    --name pharmacy-stock-alert \
    -p 5001:5000 \
    -v $(pwd)/app/data:/app/data \
    pharmacy-stock-alert
```

### 3. Verify Health Check
```bash
curl http://localhost:5001/health
```
Access the application on [http://localhost:5001](http://localhost:5001).

---

## ⚙️ Jenkins CI/CD Automation

The `Jenkinsfile` orchestrates 8 automated stages:

1. **Stage 1: Checkout:** Fetches the latest source code from GitHub `main`.
2. **Stage 2: Validate:** Runs `py_compile` syntax checks and executes all 19 Pytest tests.
3. **Stage 3: Docker Build:** Compiles the container for target `linux/amd64` architecture.
4. **Stage 4: ECR Authentication:** Securely fetches temporary authentication token via `aws ecr get-login-password`.
5. **Stage 5: Push Image:** Tags and pushes both `:latest` and `:build-${BUILD_NUMBER}` to Amazon ECR.
6. **Stage 6: Deployment to EC2 via AWS SSM:** Dispatches remote execution via AWS Systems Manager Run Command (`AWS-RunShellScript`), stopping any previous container, pulling the fresh image, and launching the new container with persistent storage.
7. **Stage 7: Verification:** Queries EC2 to verify the container is running and polls `http://127.0.0.1:5001/health` until HTTP 200 is confirmed.
8. **Stage 8: Deployment Summary:** Extracts EC2 public IP and displays deployment status.

### GitHub Webhook Configuration (Optional Automatic Push Trigger)
To trigger the Jenkins pipeline on every git push:
1. Navigate to your GitHub repository: `https://github.com/kalyan4512-tech/pharmacy-stock-alert/settings/hooks`
2. Click **Add webhook**.
3. **Payload URL:** `http://<YOUR-JENKINS-HOST>:8080/github-webhook/`
4. **Content type:** `application/json`
5. Select **Just the push event** and click **Add webhook**.

---

## ☁️ AWS Cloud Infrastructure (ECR, EC2, SSM)

- **AWS Region:** `us-east-1`
- **ECR Repository:** `724270903230.dkr.ecr.us-east-1.amazonaws.com/pharmacy-stock-alert`
- **EC2 Instance ID:** `i-090065bd6065310a0`
- **Security Group:** `pharmacy-stock-sg` (Port 5001 Inbound TCP Allowed)
- **Deployment Mechanism:** AWS Systems Manager (SSM) Run Command (Zero SSH keys stored or required).
- **Persistent Storage:** EC2 Host Volume `/home/ec2-user/pharmacy-data` mapped to container `/app/data`.

---

## 🧪 Automated Testing & QA

Run the test suite locally:
```bash
.venv/bin/pytest tests/ -v
```

### Test Coverage Highlights:
- `test_stock_status_out_of_stock`: Verifies zero quantity generates `OUT_OF_STOCK` alert.
- `test_stock_status_low_stock`: Verifies threshold triggering (`quantity <= min_threshold`).
- `test_expiry_status_expired`: Validates past dates trigger `EXPIRED` status.
- `test_expiry_status_expiring_soon`: Validates 30-day window logic.
- `test_dashboard_metrics_aggregation`: Ensures dynamic counting and financial valuation accuracy.
- `test_health_check_endpoint`: Verifies JSON health check structure and DB connectivity.
- `test_add_medicine_crud`, `test_edit_medicine_crud`, `test_delete_medicine_crud`: Full database CRUD verification.
- `test_reports_and_export`: Verifies CSV report generation and headers.
