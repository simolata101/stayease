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

    # Relationship to image set / cottage interior gallery
    images = db.relationship('AccommodationImage', backref='accommodation', cascade='all, delete-orphan', order_by='AccommodationImage.display_order.asc()')

    @property
    def interior_images(self):
        imgs = [img for img in self.images if img.is_interior]
        return imgs if imgs else self.images

    def get_all_images(self):
        if self.images and len(self.images) > 0:
            return self.images
        if self.image_url:
            return [{'image_url': self.image_url, 'title': self.name, 'caption': self.description, 'is_interior': False}]
        return [{'image_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80', 'title': self.name, 'caption': 'Resort Cottage', 'is_interior': False}]


class AccommodationImage(db.Model):
    __tablename__ = 'accommodation_images'
    
    id = db.Column(db.Integer, primary_key=True)
    accommodation_unit_id = db.Column(db.Integer, db.ForeignKey('accommodation_units.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    title = db.Column(db.String(100), default='Cottage Interior')
    caption = db.Column(db.String(255))
    is_interior = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<AccommodationImage {self.title or self.id}>'

