from datetime import datetime, date
from decimal import Decimal
from flask import Blueprint, render_template, redirect, url_for, flash, request, g
from sqlalchemy import or_
from app import db
from app.models import User, Resort, AccommodationUnit, AccommodationImage, Booking, BlockedDate, Payment, GalleryItem
from app.routes.auth import admin_required
from app.services import BookingService, AvailabilityService, PaymentService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_bookings = Booking.query.count()
    pending_bookings = Booking.query.filter_by(booking_status='pending').count()
    approved_bookings = Booking.query.filter_by(booking_status='approved').count()
    cancelled_bookings = Booking.query.filter_by(booking_status='cancelled').count()
    
    # Total payments received from DB
    payments_sum = db.session.query(db.func.sum(Payment.amount)).scalar() or Decimal('0.00')
    
    # Recent bookings
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    
    return render_template(
        'admin/dashboard.html',
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        approved_bookings=approved_bookings,
        cancelled_bookings=cancelled_bookings,
        payments_sum=payments_sum,
        recent_bookings=recent_bookings
    )

@admin_bp.route('/bookings')
@admin_required
def bookings():
    status_filter = request.args.get('status')
    search_query = request.args.get('search')
    
    query = Booking.query.join(User, Booking.customer_id == User.id)
    
    if status_filter:
        query = query.filter(Booking.booking_status == status_filter)
        
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Booking.booking_reference.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )
        
    all_bookings = query.order_by(Booking.created_at.desc()).all()
    
    bookings_data = []
    for b in all_bookings:
        payment_summary = PaymentService.get_booking_payment_summary(b.id)
        bookings_data.append({
            'booking': b,
            'payment_summary': payment_summary
        })

    return render_template(
        'admin/bookings.html',
        bookings=bookings_data,
        status_filter=status_filter,
        search_query=search_query
    )

@admin_bp.route('/booking/<int:booking_id>')
@admin_required
def booking_detail(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('admin.bookings'))

    payment_summary = PaymentService.get_booking_payment_summary(booking.id)
    return render_template('admin/booking_detail.html', booking=booking, payment_summary=payment_summary, date=date)

@admin_bp.route('/booking/<int:booking_id>/approve', methods=['POST'])
@admin_required
def approve_booking(booking_id):
    success, msg = BookingService.approve_booking(booking_id, g.user.id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('admin.booking_detail', booking_id=booking_id))

@admin_bp.route('/booking/<int:booking_id>/reject', methods=['POST'])
@admin_required
def reject_booking(booking_id):
    reason = request.form.get('reason')
    success, msg = BookingService.reject_booking(booking_id, g.user.id, reason)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('admin.booking_detail', booking_id=booking_id))

@admin_bp.route('/booking/<int:booking_id>/record-payment', methods=['POST'])
@admin_required
def record_payment(booking_id):
    amount = request.form.get('amount')
    payment_method = request.form.get('payment_method')
    payment_date_str = request.form.get('payment_date')
    payment_ref = request.form.get('payment_reference')

    try:
        payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        payment, msg = PaymentService.record_payment(
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            payment_date=payment_date,
            recorded_by_id=g.user.id,
            payment_reference=payment_ref
        )
        if payment:
            flash(msg, 'success')
        else:
            flash(msg, 'danger')
    except ValueError:
        flash('Invalid payment date format.', 'danger')

    return redirect(url_for('admin.booking_detail', booking_id=booking_id))

@admin_bp.route('/availability', methods=['GET', 'POST'])
@admin_required
def availability():
    if request.method == 'POST':
        unit_id_str = request.form.get('accommodation_unit_id')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        reason = request.form.get('reason')

        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            unit_id = int(unit_id_str) if unit_id_str and unit_id_str != '0' else None

            if start_date > end_date:
                flash('Start date must be earlier than or equal to end date.', 'danger')
            else:
                # Check if blocking dates conflict with existing active reservations
                query = Booking.query.filter(
                    Booking.booking_status.in_(['pending', 'approved']),
                    Booking.check_in_date <= end_date,
                    Booking.check_out_date > start_date
                )
                if unit_id:
                    query = query.filter(Booking.accommodation_unit_id == unit_id)

                conflicting_booking = query.first()
                if conflicting_booking:
                    flash(f"Cannot block dates! Conflicts with existing active reservation ({conflicting_booking.booking_reference}). Please resolve or cancel reservation first.", 'danger')
                else:
                    blocked = BlockedDate(
                        accommodation_unit_id=unit_id,
                        start_date=start_date,
                        end_date=end_date,
                        reason=reason,
                        created_by_id=g.user.id
                    )
                    db.session.add(blocked)
                    db.session.commit()
                    flash('Blocked date range added successfully.', 'success')
        except ValueError:
            flash('Invalid date input.', 'danger')

    blocked_dates = BlockedDate.query.order_by(BlockedDate.start_date.desc()).all()
    accommodations = AccommodationUnit.query.filter_by(is_active=True).all()
    bookings = Booking.query.filter(Booking.booking_status.in_(['pending', 'approved'])).all()

    return render_template(
        'admin/availability.html',
        blocked_dates=blocked_dates,
        accommodations=accommodations,
        bookings=bookings
    )

@admin_bp.route('/availability/unblock/<int:blocked_id>', methods=['POST'])
@admin_required
def unblock_date(blocked_id):
    blocked = db.session.get(BlockedDate, blocked_id)
    if blocked:
        db.session.delete(blocked)
        db.session.commit()
        flash('Blocked date entry removed.', 'success')
    return redirect(url_for('admin.availability'))

@admin_bp.route('/accommodations', methods=['GET', 'POST'])
@admin_required
def accommodations():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        capacity = int(request.form.get('capacity', 2))
        nightly_rate = Decimal(request.form.get('nightly_rate', '1000.00'))

        unit = AccommodationUnit(
            name=name,
            description=description,
            capacity=capacity,
            nightly_rate=nightly_rate,
            is_active=True
        )
        db.session.add(unit)
        db.session.commit()
        flash(f"Accommodation unit '{name}' created successfully.", 'success')
        return redirect(url_for('admin.accommodations'))

    units = AccommodationUnit.query.all()
    return render_template('admin/accommodations.html', units=units)

@admin_bp.route('/accommodations/<int:unit_id>/toggle', methods=['POST'])
@admin_required
def toggle_accommodation(unit_id):
    unit = db.session.get(AccommodationUnit, unit_id)
    if not unit:
        flash('Accommodation unit not found.', 'danger')
        return redirect(url_for('admin.accommodations'))

    unit.is_active = not unit.is_active
    db.session.commit()
    status_str = "activated" if unit.is_active else "deactivated"
    flash(f"Accommodation unit '{unit.name}' has been {status_str}.", 'info')
    return redirect(url_for('admin.accommodations'))

@admin_bp.route('/accommodations/<int:unit_id>/delete', methods=['POST'])
@admin_required
def delete_accommodation(unit_id):
    unit = db.session.get(AccommodationUnit, unit_id)
    if not unit:
        flash('Accommodation unit not found.', 'danger')
        return redirect(url_for('admin.accommodations'))

    # SAFEGUARD: Check if there are active, pending, approved, ongoing, or future paid bookings tied to this unit
    active_bookings = Booking.query.filter(
        Booking.accommodation_unit_id == unit_id,
        Booking.booking_status.in_(['pending', 'approved']),
        Booking.check_out_date >= date.today()
    ).all()

    if active_bookings:
        flash(
            f"PROTECTION TRIGGERED: Cannot delete '{unit.name}'. "
            f"There are {len(active_bookings)} active/ongoing or upcoming paid reservations associated with this unit. "
            f"Please cancel or complete those reservations before deleting.",
            "danger"
        )
        return redirect(url_for('admin.accommodations'))

    db.session.delete(unit)
    db.session.commit()
    flash(f"Accommodation unit '{unit.name}' deleted successfully.", 'success')
    return redirect(url_for('admin.accommodations'))

@admin_bp.route('/resort-settings', methods=['GET', 'POST'])
@admin_required
def resort_settings():
    resort = Resort.query.first()
    if not resort:
        resort = Resort(name="StayEase Resort")
        db.session.add(resort)
        db.session.commit()

    if request.method == 'POST':
        resort.name = request.form.get('name')
        resort.description = request.form.get('description')
        resort.location = request.form.get('location')
        resort.contact_email = request.form.get('contact_email')
        resort.contact_phone = request.form.get('contact_phone')
        resort.policies = request.form.get('policies')
        resort.hero_image_url = request.form.get('hero_image_url')
        
        db.session.commit()
        flash('Resort settings and front-end infrastructure updated successfully.', 'success')
        return redirect(url_for('admin.resort_settings'))

    return render_template('admin/resort_settings.html', resort=resort)

@admin_bp.route('/customers')
@admin_required
def customers():
    customer_list = User.query.filter_by(role='customer').order_by(User.created_at.desc()).all()
    return render_template('admin/customers.html', customers=customer_list)

@admin_bp.route('/gallery', methods=['GET', 'POST'])
@admin_required
def gallery():
    active_tab = request.args.get('active_tab', 'cottages')

    if request.method == 'POST':
        title = request.form.get('title')
        caption = request.form.get('caption')
        image_url = request.form.get('image_url')
        category = request.form.get('category', 'General')
        display_order = int(request.form.get('display_order', 0))

        if not title or not image_url:
            flash('Title and Image URL are required.', 'danger')
        else:
            item = GalleryItem(
                title=title,
                caption=caption,
                image_url=image_url,
                category=category,
                display_order=display_order,
                is_active=True
            )
            db.session.add(item)
            db.session.commit()
            flash(f"Gallery photo '{title}' added successfully.", 'success')
            return redirect(url_for('admin.gallery', active_tab='general'))

    items = GalleryItem.query.order_by(GalleryItem.display_order.asc(), GalleryItem.created_at.desc()).all()
    accommodations = AccommodationUnit.query.all()
    return render_template('admin/gallery.html', items=items, accommodations=accommodations, active_tab=active_tab)

@admin_bp.route('/gallery/<int:item_id>/toggle', methods=['POST'])
@admin_required
def toggle_gallery_item(item_id):
    item = db.session.get(GalleryItem, item_id)
    if item:
        item.is_active = not item.is_active
        db.session.commit()
        status_str = "published" if item.is_active else "hidden"
        flash(f"Gallery photo '{item.title}' is now {status_str}.", 'info')
    return redirect(url_for('admin.gallery', active_tab='general'))

@admin_bp.route('/gallery/<int:item_id>/delete', methods=['POST'])
@admin_required
def delete_gallery_item(item_id):
    item = db.session.get(GalleryItem, item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        flash(f"Gallery photo '{item.title}' deleted.", 'success')
    return redirect(url_for('admin.gallery', active_tab='general'))

@admin_bp.route('/gallery/cottage-image/add', methods=['POST'])
@admin_required
def add_cottage_image():
    unit_id = request.form.get('accommodation_unit_id')
    title = request.form.get('title')
    caption = request.form.get('caption')
    image_url = request.form.get('image_url')
    is_interior = request.form.get('is_interior') == '1'
    display_order = int(request.form.get('display_order', 0))

    if not unit_id or not image_url:
        flash('Cottage choice package and Image URL are required.', 'danger')
    else:
        img = AccommodationImage(
            accommodation_unit_id=int(unit_id),
            title=title or 'Cottage Interior',
            caption=caption,
            image_url=image_url,
            is_interior=is_interior,
            display_order=display_order
        )
        db.session.add(img)
        db.session.commit()
        flash('New interior photo added to cottage package.', 'success')

    return redirect(url_for('admin.gallery', active_tab='cottages'))

@admin_bp.route('/gallery/cottage-image/<int:image_id>/edit', methods=['POST'])
@admin_required
def edit_cottage_image(image_id):
    img = db.session.get(AccommodationImage, image_id)
    if not img:
        flash('Cottage photo not found.', 'danger')
        return redirect(url_for('admin.gallery', active_tab='cottages'))

    title = request.form.get('title')
    caption = request.form.get('caption')
    image_url = request.form.get('image_url')
    is_interior = request.form.get('is_interior') == '1'

    if not image_url:
        flash('Image URL cannot be empty.', 'danger')
    else:
        img.title = title
        img.caption = caption
        img.image_url = image_url
        img.is_interior = is_interior
        db.session.commit()
        flash(f"Cottage photo '{img.title or image_id}' updated/replaced successfully.", 'success')

    return redirect(url_for('admin.gallery', active_tab='cottages'))

@admin_bp.route('/gallery/cottage-image/<int:image_id>/delete', methods=['POST'])
@admin_required
def delete_cottage_image(image_id):
    img = db.session.get(AccommodationImage, image_id)
    if img:
        db.session.delete(img)
        db.session.commit()
        flash('Cottage photo removed from package image set.', 'success')
    return redirect(url_for('admin.gallery', active_tab='cottages'))


