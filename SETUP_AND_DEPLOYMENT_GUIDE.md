# StayEase — Local Setup & Railway Deployment Manuscript

This document serves as an exhaustive, step-by-step technical manuscript for configuring, running, and deploying **StayEase — Resort and Hotel Booking Management System** both locally for development and in production using **Railway.app** (or similar cloud PaaS environments).

---

## 1. System Overview & Architecture

StayEase is built using Python (Flask) with SQLAlchemy ORM, Jinja2 templating, and Bootstrap 5 frontend styling.

```
+-------------------------------------------------------------------+
|                        Client Browser                             |
+-------------------------------------------------------------------+
                                 |
                                 v
+-------------------------------------------------------------------+
|               Gunicorn WSGI / Flask Dev Server                    |
+-------------------------------------------------------------------+
                                 |
        +------------------------+------------------------+
        |                                                 |
        v                                                 v
+-----------------------+                         +-----------------------+
|  StayEase App Logic   |                         |  Database Engine      |
|  (Blueprints/Services)|                         |  (SQLite / MySQL /    |
+-----------------------+                         |   PostgreSQL)         |
        |                                         +-----------------------+
        v
+-----------------------+
| Flask-Mail (SMTP)     |
+-----------------------+
```

---

## 2. Local Setup Guide (Step-by-Step)

### Prerequisites
- **Python**: Version 3.10+ (Tested on Python 3.14)
- **Pip** and `virtualenv`
- **Git**

### Step 1: Clone Repository & Create Virtual Environment

```bash
# Clone repository or navigate to directory
cd /config/Desktop/Hotel

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows PowerShell:
# .\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Local Environment Variables

Create a `.env` file in the root directory:

```ini
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here-change-in-production

# SQLite database for local development
DATABASE_URL=sqlite:///stayease.db

# Optional: Email SMTP settings (Leave empty for fallback mode)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 4: Initialize & Seed Database

```bash
# Create database tables and default resort record
python cli.py db-init

# Seed demo accounts (Admin & Customer), accommodations, and sample booking
python cli.py seed-demo
```

### Step 5: Run Local Server

```bash
python run.py
```

Access the application in your browser at `http://127.0.0.1:5000`.

#### Local Accounts Created by Seed Script:
- **Administrator**: `admin@stayease.com` / `Admin123!`
- **Customer**: `customer@stayease.com` / `Customer123!`

### Step 6: Execute Automated Test Suite

```bash
PYTHONPATH=. pytest -v tests/
```

---

## 3. Railway.app Cloud Deployment Guide

Railway is a modern Cloud Application Platform (PaaS) ideal for deploying Flask web applications with database plugins.

### Step 1: Prepare Repository for Railway
Ensure the following deployment files exist in your repository root (already provided):
- **`Procfile`**: Specifies the Gunicorn command.
  ```
  web: gunicorn run:app
  ```
- **`requirements.txt`**: Includes `gunicorn` and required database drivers (`PyMySQL` / `psycopg2-binary`).

### Step 2: Create a New Project on Railway
1. Sign in to your [Railway.app](https://railway.app) account.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your `StayEase` repository.

### Step 3: Provision a Database Plugin on Railway
1. Inside your Railway Project Canvas, click **New** → **Database**.
2. Select **Add MySQL** (or **Add PostgreSQL**).
3. Railway will provision a database instance and automatically export database environment variables.

### Step 4: Set Environment Variables on Railway
In your Railway Service Settings under the **Variables** tab, add the following key-value pairs:

| Variable Name | Example Value / Railway Template | Explanation |
| :--- | :--- | :--- |
| `SECRET_KEY` | `generate-a-strong-random-secret-key` | Session security |
| `DATABASE_URL` | `${{MySQL.MYSQL_URL}}` (or `${{PostgreSQL.POSTGRES_URL}}`) | Connects Flask to Railway DB |
| `FLASK_ENV` | `production` | Production mode |
| `MAIL_SERVER` | `smtp.sendgrid.net` | (Optional) Email host |
| `MAIL_PORT` | `587` | (Optional) SMTP Port |
| `MAIL_USE_TLS` | `True` | TLS Security |
| `MAIL_USERNAME` | `apikey` | SMTP Username |
| `MAIL_PASSWORD` | `your-sendgrid-api-key` | SMTP Password |

*Note on Database URLs*: If using MySQL with PyMySQL, format the URL as `mysql+pymysql://user:password@host:port/dbname`.

### Step 5: Automatic Database Migration & Seeding on Build/Start
In Railway Service Settings under **Deploy** → **Start Command**, set:

```bash
python cli.py db-init && python cli.py seed-demo && gunicorn run:app
```

This guarantees database tables and initial administrator accounts are generated automatically upon deployment.

### Step 6: Expose Public Networking & Custom Domain
1. In Railway Service Settings, navigate to **Networking**.
2. Click **Generate Domain** to get a free `*.up.railway.app` SSL-secured web domain.
3. (Optional) Click **Custom Domain** to attach your own domain name (e.g., `reservations.myresort.com`).

---

## 4. Operational Maintenance & Monitoring

- **Viewing Application Logs**: In Railway, open the **Logs** tab of your deployment service to monitor incoming HTTP requests, Gunicorn worker outputs, and application notifications.
- **Handling Database Migrations**: When changing database schemas in future updates, use Flask-Migrate CLI commands:
  ```bash
  flask db migrate -m "Added new field"
  flask db upgrade
  ```
