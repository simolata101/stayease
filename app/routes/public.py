from datetime import datetime, date
from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.models import Resort, AccommodationUnit, GalleryItem
from app.services import AvailabilityService
from app.forms import AvailabilitySearchForm

public_bp = Blueprint('public', __name__)


@public_bp.route('/', methods=['GET', 'POST'])
def index():
    resort = Resort.query.first()
    accommodations = AccommodationUnit.query.filter_by(is_active=True).all()
    form = AvailabilitySearchForm()
    
    search_results = None
    searched = False
    
    # Handle GET query params if passed from header or search redirect
    check_in_str = request.args.get('check_in') or request.form.get('check_in')
    check_out_str = request.args.get('check_out') or request.form.get('check_out')
    guests_str = request.args.get('guests') or request.form.get('guests')
    
    if check_in_str and check_out_str:
        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            guests = int(guests_str or 2)
            
            searched = True
            
            if check_in < date.today():
                flash('Check-in date cannot be in the past.', 'warning')
            elif check_in >= check_out:
                flash('Check-in date must be earlier than check-out date.', 'warning')
            else:
                search_results = []
                for unit in accommodations:
                    if guests > unit.capacity:
                        continue
                    available, reason = AvailabilityService.is_unit_available(unit.id, check_in, check_out)
                    search_results.append({
                        'unit': unit,
                        'available': available,
                        'reason': reason,
                        'nights': (check_out - check_in).days,
                        'estimated_total': unit.nightly_rate * (check_out - check_in).days
                    })
        except ValueError:
            flash('Invalid date format provided.', 'danger')

    return render_template(
        'public/index.html',
        resort=resort,
        accommodations=accommodations,
        form=form,
        searched=searched,
        search_results=search_results,
        check_in_str=check_in_str,
        check_out_str=check_out_str,
        guests_str=guests_str
    )

@public_bp.route('/gallery')
def gallery():
    resort = Resort.query.first()
    items = GalleryItem.query.filter_by(is_active=True).order_by(GalleryItem.display_order.asc(), GalleryItem.created_at.desc()).all()
    return render_template('public/gallery.html', resort=resort, items=items)


@public_bp.route('/contact')
def contact():
    resort = Resort.query.first()
    return render_template('public/contact.html', resort=resort)
