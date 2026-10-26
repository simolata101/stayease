from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, g
from app import db
from app.models import User
from app.forms.auth_forms import RegistrationForm, LoginForm, ProfileForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        user = db.session.get(User, session['user_id'])
        if not user or user.role != 'admin':
            flash('Administrator access required.', 'danger')
            return redirect(url_for('public.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('public.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email address already registered.', 'danger')
            return render_template('auth/register.html', form=form)
        
        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            contact_number=form.contact_number.data,
            role='customer'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if g.user:
        return redirect(url_for('public.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.account_status != 'active':
                flash('This account is suspended.', 'danger')
                return render_template('auth/login.html', form=form)
                
            session.clear()
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('admin.dashboard') if user.role == 'admin' else url_for('customer.my_bookings')
                
            return redirect(next_page)
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.index'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = g.user
    form = ProfileForm(obj=user)
    if form.validate_on_submit():
        existing = User.query.filter(User.email == form.email.data, User.id != user.id).first()
        if existing:
            flash('This email address is already in use by another account.', 'danger')
            return render_template('auth/profile.html', form=form)
        
        user.full_name = form.full_name.data
        user.email = form.email.data
        user.contact_number = form.contact_number.data
        
        if form.new_password.data:
            if len(form.new_password.data) < 6:
                flash('New password must be at least 6 characters long.', 'danger')
                return render_template('auth/profile.html', form=form)
            user.set_password(form.new_password.data)
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
        
    return render_template('auth/profile.html', form=form)

