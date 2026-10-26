from datetime import datetime, timezone
from app import db

class BlockedDate(db.Model):
    __tablename__ = 'blocked_dates'
    
    id = db.Column(db.Integer, primary_key=True)
    accommodation_unit_id = db.Column(db.Integer, db.ForeignKey('accommodation_units.id'), nullable=True) # Nullable for resort-wide closures
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(255))
    
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    accommodation = db.relationship('AccommodationUnit', backref='blocked_dates')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
