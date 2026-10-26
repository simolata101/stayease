# StayEase — Local Setup & Troubleshooting Guide

This guide provides step-by-step instructions for setting up and running **StayEase Resort** on Windows, macOS, and Linux, along with contingency plans for common setup errors on Windows.

---

## 🚀 Quick Setup Instructions

### **1. Prerequisites**
- **Python 3.9 – 3.12** *(Recommended)* or **Python 3.14**
  - *Windows Tip:* Ensure you check **"Add python.exe to PATH"** during installation.
- **Git**

---

### **2. Installation Steps (Windows - PowerShell / Command Prompt)**

```powershell
# Step 1: Clone the repository
git clone https://github.com/simolata101/stayease.git
cd stayease

# Step 2: Create a virtual environment
python -m venv venv

# Step 3: Activate the virtual environment
.\venv\Scripts\Activate

# Step 4: Install dependencies
pip install -r requirements.txt

# Step 5: Initialize SQLite Database & Seed Demo Data
python cli.py db-init
python cli.py seed-demo

# Step 6: Start local server
python run.py
```

Access the app in your browser at: **`http://127.0.0.1:5000`**

---

## 🛠️ Contingency Plan & Windows Troubleshooting Guide

If you encounter any issues during local installation on Windows, follow these solutions:

---

### ❌ **Issue 1: `psycopg2-binary` Build Error (`pg_config executable not found`)**

#### **Symptom:**
```text
error: subprocess-exited-with-error
Error: pg_config executable not found.
ERROR: Failed to build 'psycopg2-binary' when getting requirements to build wheel
```

#### **Root Cause:**
`psycopg2-binary` is PostgreSQL's driver. When running Python 3.13 or 3.14 on Windows, PyPI may not have pre-compiled binary wheels available for newer Python versions, causing `pip` to attempt building from C source code without PostgreSQL build tools.

#### **Contingency Solution A (Recommended for Local Dev):**
Local development uses **SQLite**, so PostgreSQL drivers are not required. Install all application dependencies directly without PostgreSQL dependencies:

```powershell
pip install Flask Flask-WTF Flask-SQLAlchemy Flask-Migrate Flask-Mail email-validator python-dotenv pytest pytest-flask Werkzeug
```

After running this command, proceed directly to:
```powershell
python cli.py db-init
python cli.py seed-demo
python run.py
```

#### **Contingency Solution B:**
Upgrade `pip` to allow fetching newer pre-compiled wheel packages:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### **Contingency Solution C:**
Re-create your virtual environment using Python 3.11 or Python 3.12, which have fully compatible pre-compiled binary wheels for `psycopg2-binary`.

---

### ❌ **Issue 2: PowerShell Script Execution Restricted**

#### **Symptom:**
```text
.\venv\Scripts\Activate : File C:\...\Activate.ps1 cannot be loaded because running scripts is disabled on this system.
```

#### **Contingency Solution:**
Run this command in PowerShell to temporarily allow virtual environment activation for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate
```

---

### ❌ **Issue 3: `python` or `pip` Command Not Recognized in Windows**

#### **Symptom:**
```text
'python' is not recognized as an internal or external command...
```

#### **Contingency Solution:**
Use the Python launcher `py` instead:
```powershell
py -m venv venv
.\venv\Scripts\Activate
py -m pip install -r requirements.txt
py cli.py db-init
py cli.py seed-demo
py run.py
```

---

## 🔑 Demo Account Credentials

Once the application is running, use these credentials to log in:

| Role | Email | Password | Access URL |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@stayease.com` | `Admin123!` | `http://127.0.0.1:5000/auth/login` |
| **Customer** | `customer@stayease.com` | `Customer123!` | `http://127.0.0.1:5000/auth/login` |

---

## 🧪 Running Automated Unit Tests

To verify that all application features, double-booking prevention logic, and gallery image sets work as expected:

```powershell
PYTHONPATH=. pytest -v tests/
```
