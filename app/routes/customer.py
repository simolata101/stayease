from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, g, abort
from app import db
from app.models import AccommodationUnit, Booking
from app.routes.auth import login_required
from app.forms import BookingForm
from app.services import BookingService, AvailabilityService, PaymentService

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

@customer_bp.route('/book/<int:unit_id>', methods=['GET', 'POST'])
@login_required
def book(unit_id):
    unit = db.session.get(AccommodationUnit, unit_id)
    if not unit or not unit.is_active:
        flash('Selected accommodation is not available for booking.', 'danger')
        return redirect(url_for('public.index'))

    form = BookingForm()
    
    # Populate unit select list
    active_units = AccommodationUnit.query.filter_by(is_active=True).all()
    form.accommodation_unit_id.choices = [(u.id, f"{u.name} (Max {u.capacity} guests - ₱{u.nightly_rate:,.2f}/night)") for u in active_units]
    
    if request.method == 'GET':
        form.accommodation_unit_id.data = unit.id
        check_in_str = request.args.get('check_in')
        check_out_str = request.args.get('check_out')
        guests_str = request.args.get('guests')
        
        if check_in_str:
            try:
                form.check_in.data = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if check_out_str:
            try:
                form.check_out.data = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        if guests_str:
            try:
                form.guests.data = int(guests_str)
            except ValueError:
                form.guests.data = 2
        else:
            form.guests.data = 2

    if form.validate_on_submit():
        selected_unit_id = form.accommodation_unit_id.data
        check_in = form.check_in.data
        check_out = form.check_out.data
        guests = form.guests.data
        special_requests = form.special_requests.data

        booking, msg = BookingService.create_booking(
            customer_id=g.user.id,
            accommodation_unit_id=selected_unit_id,
            check_in=check_in,
            check_out=check_out,
            guest_count=guests,
            special_requests=special_requests
        )

        if booking:
            flash(msg, 'success')
            return redirect(url_for('customer.confirmation', reference=booking.booking_reference))
        else:
            flash(msg, 'danger')

    return render_template('customer/book.html', form=form, unit=unit)

@customer_bp.route('/confirmation/<string:reference>')
@login_required
def confirmation(reference):
    booking = Booking.query.filter_by(booking_reference=reference, customer_id=g.user.id).first_or_404()
    payment_summary = PaymentService.get_booking_payment_summary(booking.id)
    return render_template('customer/confirmation.html', booking=booking, payment_summary=payment_summary)

@customer_bp.route('/my-bookings')
@login_required
def my_bookings():
    user_bookings = Booking.query.filter_by(customer_id=g.user.id).order_by(Booking.created_at.desc()).all()
    
    # Attach payment summaries
    bookings_with_payment = []
    for b in user_bookings:
        payment_summary = PaymentService.get_booking_payment_summary(b.id)
        bookings_with_payment.append({
            'booking': b,
            'payment_summary': payment_summary
        })

    return render_template('customer/my_bookings.html', bookings=bookings_with_payment)

@customer_bp.route('/booking/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.customer_id != g.user.id:
        flash('Booking not found or access denied.', 'danger')
        return redirect(url_for('customer.my_bookings'))

    payment_summary = PaymentService.get_booking_payment_summary(booking.id)
    return render_template('customer/booking_detail.html', booking=booking, payment_summary=payment_summary)

@customer_bp.route('/cancel-booking/<int:booking_id>', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.customer_id != g.user.id:
        flash('Booking not found or access denied.', 'danger')
        return redirect(url_for('customer.my_bookings'))

    reason = request.form.get('reason', 'Cancelled by customer.')
    success, msg = BookingService.cancel_booking(booking_id, g.user.id, reason)
    
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')

    return redirect(url_for('customer.booking_detail', booking_id=booking_id))
