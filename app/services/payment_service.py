from decimal import Decimal
from app import db
from app.models import Payment, Booking

class PaymentService:
    @staticmethod
    def get_booking_payment_summary(booking_id):
        """Calculates total paid, outstanding balance, and payment status for a booking."""
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return None

        payments = Payment.query.filter_by(booking_id=booking_id).all()
        total_paid = sum((Decimal(p.amount) for p in payments), Decimal('0.00'))
        total_price = Decimal(booking.total_price)
        outstanding_balance = total_price - total_paid

        if total_paid <= 0:
            payment_status = 'Unpaid'
        elif total_paid < total_price:
            payment_status = 'Partially Paid'
        else:
            payment_status = 'Paid'

        return {
            'total_price': total_price,
            'total_paid': total_paid,
            'outstanding_balance': max(Decimal('0.00'), outstanding_balance),
            'payment_status': payment_status,
            'payments': payments
        }

    @staticmethod
    def record_payment(booking_id, amount, payment_method, payment_date, recorded_by_id, payment_reference=None):
        """Records a manual payment transaction."""
        booking = db.session.get(Booking, booking_id)
        if not booking:
            return None, "Booking not found."

        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            return None, "Payment amount must be greater than zero."

        payment = Payment(
            booking_id=booking_id,
            amount=amount_decimal,
            payment_method=payment_method,
            payment_reference=payment_reference,
            payment_date=payment_date,
            recorded_by_id=recorded_by_id
        )

        db.session.add(payment)
        db.session.commit()

        summary = PaymentService.get_booking_payment_summary(booking_id)
        return payment, f"Payment of ₱{amount_decimal:,.2f} recorded successfully. Current status: {summary['payment_status']}."
