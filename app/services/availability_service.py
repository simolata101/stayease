from datetime import date
from sqlalchemy import or_
from app import db
from app.models import AccommodationUnit, Booking, BlockedDate

class AvailabilityService:
    @staticmethod
    def is_unit_available(accommodation_unit_id, check_in, check_out, exclude_booking_id=None):
        """
        Checks whether an accommodation unit is available for the half-open interval [check_in, check_out).
        Half-open interval means checkout on May 10 allows a new checkin on May 10.
        Overlapping condition: (Booking.check_in_date < check_out) AND (Booking.check_out_date > check_in)
        Blocks on booking status IN ('pending', 'approved').
        Also checks blocked dates.
        """
        if check_in >= check_out:
            return False, "Check-in date must be earlier than check-out date."

        if check_in < date.today():
            return False, "Check-in date cannot be in the past."

        # Check existing active bookings for overlap
        booking_query = Booking.query.filter(
            Booking.accommodation_unit_id == accommodation_unit_id,
            Booking.booking_status.in_(['pending', 'approved']),
            Booking.check_in_date < check_out,
            Booking.check_out_date > check_in
        )

        if exclude_booking_id:
            booking_query = booking_query.filter(Booking.id != exclude_booking_id)

        overlapping_booking = booking_query.first()
        if overlapping_booking:
            return False, f"The selected unit is reserved or pending reservation for these dates (Reference: {overlapping_booking.booking_reference})."

        # Check blocked dates (maintenance / operational closures)
        # BlockedDate end_date is inclusive in traditional maintenance windows, so interval is [start_date, end_date + 1 day)
        blocked_query = BlockedDate.query.filter(
            or_(
                BlockedDate.accommodation_unit_id == accommodation_unit_id,
                BlockedDate.accommodation_unit_id.is_(None) # Resort-wide closure
            ),
            BlockedDate.start_date < check_out,
            BlockedDate.end_date >= check_in
        ).first()

        if blocked_query:
            reason_str = f" ({blocked_query.reason})" if blocked_query.reason else ""
            return False, f"The resort or selected unit is closed/blocked for maintenance during requested dates{reason_str}."

        return True, "Unit is available."

    @staticmethod
    def get_available_units(check_in, check_out, guest_count=None):
        """
        Finds all active accommodation units that are free between check_in and check_out
        and can accommodate guest_count.
        """
        if check_in >= check_out or check_in < date.today():
            return []

        units = AccommodationUnit.query.filter_by(is_active=True).all()
        available_units = []

        for unit in units:
            if guest_count and guest_count > unit.capacity:
                continue

            available, _ = AvailabilityService.is_unit_available(unit.id, check_in, check_out)
            if available:
                available_units.append(unit)

        return available_units
