from datetime import datetime, timezone
from app import db

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    accommodation_unit_id = db.Column(db.Integer, db.ForeignKey('accommodation_units.id'), nullable=False)
    
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    guest_count = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # 'pending', 'approved', 'rejected', 'cancelled', 'completed'
    booking_status = db.Column(db.String(20), nullable=False, default='pending') 
    
    special_requests = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    
    processed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    customer = db.relationship('User', foreign_keys=[customer_id], backref='bookings')
    processed_by = db.relationship('User', foreign_keys=[processed_by_id])
    accommodation = db.relationship('AccommodationUnit', backref='bookings')
    
class BookingStatusHistory(db.Model):
    __tablename__ = 'booking_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    previous_status = db.Column(db.String(20))
    new_status = db.Column(db.String(20), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    remarks = db.Column(db.Text)
    
    booking = db.relationship('Booking', backref='status_history')
    changed_by = db.relationship('User', foreign_keys=[changed_by_id])
