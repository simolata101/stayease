from datetime import datetime, timezone
from app import db

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False) # e.g. 'Bank Transfer', 'Cash'
    payment_reference = db.Column(db.String(100))
    payment_date = db.Column(db.Date, nullable=False)
    
    recorded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    booking = db.relationship('Booking', backref='payments')
    recorded_by = db.relationship('User', foreign_keys=[recorded_by_id])
