from datetime import datetime, timezone
from app import db

class AccommodationUnit(db.Model):
    __tablename__ = 'accommodation_units'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    capacity = db.Column(db.Integer, nullable=False)
    nightly_rate = db.Column(db.Numeric(10, 2), nullable=False) # Use Decimal for monetary values
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
