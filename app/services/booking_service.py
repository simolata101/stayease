import secrets
import string
from datetime import datetime, timezone
from app import db
from app.models import Booking, BookingStatusHistory, AccommodationUnit, User
from app.services.availability_service import AvailabilityService
from app.services.notification_service import NotificationService

class BookingService:
    @staticmethod
    def generate_reference():
        """Generates a unique reference code like SE-20261026-A1B2."""
        today_str = datetime.now(timezone.utc).strftime('%Y%m%d')
        random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        ref = f"SE-{today_str}-{random_suffix}"
        
        while Booking.query.filter_by(booking_reference=ref).first() is not None:
            random_suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            ref = f"SE-{today_str}-{random_suffix}"
            
        return ref

    @staticmethod
    def create_booking(customer_id, accommodation_unit_id, check_in, check_out, guest_count, special_requests=None):
        """Creates a new booking request in pending status after verifying availability."""
        unit = db.session.get(AccommodationUnit, accommodation_unit_id)
        if not unit or not unit.is_active:
            return None, "Selected accommodation is not available."

        if guest_count > unit.capacity:
            return None, f"Guest count ({guest_count}) exceeds unit capacity ({unit.capacity})."

        is_avail, msg = AvailabilityService.is_unit_available(accommodation_unit_id, check_in, check_out)
        if not is_avail:
            return None, msg

        nights = (check_out - check_in).days
        total_price = unit.nightly_rate * nights
        ref_code = BookingService.generate_reference()

        booking = Booking(
            booking_reference=ref_code,
            customer_id=customer_id,
            accommodation_unit_id=accommodation_unit_id,
            check_in_date=check_in,
            check_out_date=check_out,
            guest_count=guest_count,
            total_price=total_price,
            booking_status='pending',
            special_requests=special_requests
        )

        db.session.add(booking)
        db.session.flush() # get booking.id for history record

        history = BookingStatusHistory(
            booking_id=booking.id,
            previous_status=None,
            new_status='pending',
            changed_by_id=customer_id,
            remarks='Booking request submitted by customer.'
        )
        db.session.add(history)
        db.session.commit()

        # Send confirmation email asynchronously / safely
        customer = db.session.get(User, customer_id)
        if customer and customer.email:
            NotificationService.send_booking_status_email(
                customer.email, 
                customer.full_name, 
                ref_code, 
                'pending', 
                f"Your booking request for {unit.name} from {check_in} to {check_out} has been received and is pending approval."
            )

        return booking, "Booking request submitted successfully!"

    @staticmethod
    def approve_booking(booking_id, admin_id):
        """
        Approves a pending booking with strict revalidation.
        Revalidates availability to ensure no conflicting booking claimed the dates.
        """
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return False, "Booking not found."

        if booking.booking_status != 'pending':
            return False, f"Cannot approve booking in '{booking.booking_status}' status. Only pending bookings can be approved."

        # Double-booking check again before approval
        is_avail, msg = AvailabilityService.is_unit_available(
            booking.accommodation_unit_id, 
            booking.check_in_date, 
            booking.check_out_date,
            exclude_booking_id=booking.id
        )

        if not is_avail:
            return False, f"Approval failed due to availability conflict: {msg}"

        old_status = booking.booking_status
        booking.booking_status = 'approved'
        booking.processed_by_id = admin_id

        history = BookingStatusHistory(
            booking_id=booking.id,
            previous_status=old_status,
            new_status='approved',
            changed_by_id=admin_id,
            remarks='Booking request approved by administrator.'
        )
        db.session.add(history)
        db.session.commit()

        # Send notification
        if booking.customer and booking.customer.email:
            NotificationService.send_booking_status_email(
                booking.customer.email,
                booking.customer.full_name,
                booking.booking_reference,
                'approved',
                f"Great news! Your reservation request for {booking.accommodation.name} ({booking.check_in_date} to {booking.check_out_date}) has been approved!"
            )

        return True, "Booking approved successfully."

    @staticmethod
    def reject_booking(booking_id, admin_id, reason=None):
        """Rejects a pending booking request."""
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return False, "Booking not found."

        if booking.booking_status != 'pending':
            return False, f"Cannot reject booking in '{booking.booking_status}' status."

        old_status = booking.booking_status
        booking.booking_status = 'rejected'
        booking.rejection_reason = reason or "No specific reason provided."
        booking.processed_by_id = admin_id

        history = BookingStatusHistory(
            booking_id=booking.id,
            previous_status=old_status,
            new_status='rejected',
            changed_by_id=admin_id,
            remarks=f"Booking rejected. Reason: {booking.rejection_reason}"
        )
        db.session.add(history)
        db.session.commit()

        # Send notification
        if booking.customer and booking.customer.email:
            NotificationService.send_booking_status_email(
                booking.customer.email,
                booking.customer.full_name,
                booking.booking_reference,
                'rejected',
                f"Your reservation request for {booking.booking_reference} was rejected. Reason: {booking.rejection_reason}"
            )

        return True, "Booking rejected."

    @staticmethod
    def cancel_booking(booking_id, user_id, reason=None):
        """Cancels an existing booking if permitted."""
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return False, "Booking not found."

        if booking.booking_status in ('cancelled', 'rejected', 'completed'):
            return False, f"Booking cannot be cancelled from '{booking.booking_status}' status."

        old_status = booking.booking_status
        booking.booking_status = 'cancelled'

        history = BookingStatusHistory(
            booking_id=booking.id,
            previous_status=old_status,
            new_status='cancelled',
            changed_by_id=user_id,
            remarks=f"Booking cancelled. Reason: {reason or 'Cancelled by user.'}"
        )
        db.session.add(history)
        db.session.commit()

        # Send notification
        if booking.customer and booking.customer.email:
            NotificationService.send_booking_status_email(
                booking.customer.email,
                booking.customer.full_name,
                booking.booking_reference,
                'cancelled',
                f"Your booking reference {booking.booking_reference} has been cancelled."
            )

        return True, "Booking cancelled successfully."
