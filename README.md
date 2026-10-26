# StayEase — Resort and Hotel Booking Management System MVP

StayEase is a centralized web application designed for resort and hotel owners to replace messy Facebook Messenger reservations, prevent double bookings, track customer payments, and manage availability efficiently.

---

## Key Features

1. **Centralized Double-Booking Prevention**:
   - Availability algorithm evaluates half-open date intervals `[check_in, check_out)`.
   - Re-evaluates availability at approval time to prevent race conditions.
   - Respects operational closures and maintenance blocks.

2. **Customer Experience**:
   - Real-time availability search with instant price estimations.
   - Reservation request submission with unique reference numbers (`SE-YYYYMMDD-XXXX`).
   - Customer account profile management and booking history tracking.

3. **Administrator Dashboard**:
   - Protected admin routes for resort owners.
   - Comprehensive dashboard statistics (Total, Pending, Approved, Payments, Balances).
   - Approval & Rejection workflow with customizable feedback/reasons.
   - Availability calendar management (block units or whole resort for maintenance).
   - Accommodation unit and rate management.
   - Resort settings, policies, and contact information editor.

4. **Payment Tracking**:
   - Manual payment recording (Cash, GCash/Bank Transfer, Credit Card, Check).
   - Outstanding balance calculation and status tracking (Unpaid, Partially Paid, Paid).

5. **Notification System**:
   - Asynchronous/safely wrapped email notifications via Flask-Mail.
   - Graceful fallback when email server is not configured.

---

## Tech Stack

- **Backend**: Python 3.14 + Flask
- **Database**: SQLAlchemy 2.0+ (SQLite for dev/testing, MySQL compatible)
- **Forms & Security**: Flask-WTF + WTForms, Werkzeug password hashing
- **Testing**: pytest & pytest-flask
- **Frontend**: HTML5, Vanilla CSS / Bootstrap 5, Jinja2

---

## Getting Started

### 1. Prerequisites & Virtual Environment

```bash
# Clone or navigate to the project directory
cd /config/Desktop/Hotel

# Activate virtual environment
source venv/bin/activate
```

### 2. Database Setup & Demo Data Seeding

```bash
# Initialize database tables and default resort settings
python cli.py db-init

# Seed demo administrator, customer, accommodations, and sample booking
python cli.py seed-demo
```

### Demo Credentials

| Role | Email | Password |
| :--- | :--- | :--- |
| **Administrator** | `admin@stayease.com` | `Admin123!` |
| **Customer** | `customer@stayease.com` | `Customer123!` |

---

## Running the Web Application

```bash
# Run local Flask development server
python run.py
```

Access the application in your browser at: `http://127.0.0.1:5000`

---

## Running Automated Tests

```bash
# Execute unit & integration test suite
PYTHONPATH=. pytest -v tests/
```

All 8 automated test cases test:
- Password hashing & security
- Customer registration & duplicate email handling
- Login/logout session workflows
- Availability calculation & half-open interval overlap checks
- Admin approval & race condition double-booking prevention
- Manual payment status summary calculations
