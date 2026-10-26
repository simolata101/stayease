from datetime import date, timedelta
from app import db
from app.models import User, AccommodationUnit, Booking, Payment, BlockedDate
from app.services import BookingService, AvailabilityService, PaymentService

def test_availability_service(app, client):
    """Test AvailabilityService logic including overlap conditions."""
    with app.app_context():
        unit = AccommodationUnit(name="Ocean Deluxe", capacity=4, nightly_rate=2500.0)
        db.session.add(unit)
        db.session.commit()

        today = date.today()
        d1 = today + timedelta(days=5)
        d2 = today + timedelta(days=10)

        # Initially available
        avail, msg = AvailabilityService.is_unit_available(unit.id, d1, d2)
        assert avail is True

        # Create booking covering d1 to d2
        cust = User(email="testcust@example.com", full_name="Test Customer", role="customer")
        cust.set_password("password123")
        db.session.add(cust)
        db.session.commit()

        booking, msg = BookingService.create_booking(
            customer_id=cust.id,
            accommodation_unit_id=unit.id,
            check_in=d1,
            check_out=d2,
            guest_count=2
        )
        assert booking is not None
        assert booking.booking_status == 'pending'

        # Attempt overlapping booking (e.g. d1+2 to d2+2)
        d_overlap_start = d1 + timedelta(days=2)
        d_overlap_end = d2 + timedelta(days=2)
        avail, msg = AvailabilityService.is_unit_available(unit.id, d_overlap_start, d_overlap_end)
        assert avail is False
        assert "reserved or pending reservation" in msg

        # Half-open check: Check-in on same day as existing checkout (d2 to d2+5) MUST BE ALLOWED
        d_next_start = d2
        d_next_end = d2 + timedelta(days=5)
        avail, msg = AvailabilityService.is_unit_available(unit.id, d_next_start, d_next_end)
        assert avail is True

def test_admin_approval_and_double_booking_rejection(app, client):
    """Test admin approval and double-booking conflict check."""
    with app.app_context():
        unit = AccommodationUnit(name="Sunset Cabin", capacity=2, nightly_rate=1500.0)
        admin = User(email="admin_test@example.com", full_name="Admin Test", role="admin")
        cust1 = User(email="cust1@example.com", full_name="Cust One", role="customer")
        cust2 = User(email="cust2@example.com", full_name="Cust Two", role="customer")
        for u in (admin, cust1, cust2):
            u.set_password("password123")
            db.session.add(u)
        db.session.add(unit)
        db.session.commit()

        d1 = date.today() + timedelta(days=15)
        d2 = date.today() + timedelta(days=18)

        b1, _ = BookingService.create_booking(cust1.id, unit.id, d1, d2, 2)
        assert b1.booking_status == 'pending'

        # Approve b1
        success, msg = BookingService.approve_booking(b1.id, admin.id)
        assert success is True
        assert b1.booking_status == 'approved'

        # Attempt to create b2 with same dates -> should fail
        b2, msg = BookingService.create_booking(cust2.id, unit.id, d1, d2, 2)
        assert b2 is None
        assert "reserved or pending" in msg

def test_manual_payment_service(app, client):
    """Test manual payment tracking & status summary."""
    with app.app_context():
        unit = AccommodationUnit(name="Garden Suite", capacity=3, nightly_rate=2000.0)
        cust = User(email="cust_pay@example.com", full_name="Pay Customer", role="customer")
        admin = User(email="admin_pay@example.com", full_name="Pay Admin", role="admin")
        cust.set_password("password123")
        admin.set_password("password123")
        db.session.add_all([unit, cust, admin])
        db.session.commit()

        d1 = date.today() + timedelta(days=20)
        d2 = date.today() + timedelta(days=23) # 3 nights = 6000.00
        booking, _ = BookingService.create_booking(cust.id, unit.id, d1, d2, 2)

        # Initial payment status = Unpaid
        summary = PaymentService.get_booking_payment_summary(booking.id)
        assert summary['payment_status'] == 'Unpaid'
        assert summary['total_paid'] == 0
        assert summary['outstanding_balance'] == 6000.00

        # Record Partial Payment of 2000
        p1, msg = PaymentService.record_payment(
            booking_id=booking.id,
            amount=2000.00,
            payment_method="GCash",
            payment_date=date.today(),
            recorded_by_id=admin.id,
            payment_reference="GC123"
        )
        assert p1 is not None
        summary = PaymentService.get_booking_payment_summary(booking.id)
        assert summary['payment_status'] == 'Partially Paid'
        assert summary['outstanding_balance'] == 4000.00

        # Record Remaining Payment of 4000
        p2, msg = PaymentService.record_payment(
            booking_id=booking.id,
            amount=4000.00,
            payment_method="Cash",
            payment_date=date.today(),
            recorded_by_id=admin.id
        )
        summary = PaymentService.get_booking_payment_summary(booking.id)
        assert summary['payment_status'] == 'Paid'
        assert summary['outstanding_balance'] == 0
