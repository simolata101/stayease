import os
import click
from app import create_app, db
from app.models import User, Resort, AccommodationUnit, Booking, GalleryItem

app = create_app()

@app.cli.command("db-init")
def db_init():
    """Create database tables."""
    db.create_all()
    print("Database tables created.")
    
    # Initialize basic resort info if it doesn't exist
    if not Resort.query.first():
        default_resort = Resort(
            name="StayEase Resort",
            description="Welcome to StayEase, your perfect tropical getaway.",
            location="123 Beachfront Drive, Paradise Island",
            contact_email="hello@stayease.test",
            contact_phone="+63 900 000 0000"
        )
        db.session.add(default_resort)
        db.session.commit()
        print("Default resort settings initialized.")

@app.cli.command("seed-admin")
@click.argument("email")
@click.argument("password")
def seed_admin(email, password):
    """Seed an administrator account."""
    if User.query.filter_by(email=email).first():
        print(f"User with email {email} already exists.")
        return
        
    admin = User(
        full_name="System Administrator",
        email=email,
        role="admin"
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    print(f"Admin account {email} created successfully.")

@app.cli.command("seed-demo")
def seed_demo():
    """Seed demo users, accommodations, and sample bookings."""
    # Seed Admin User
    admin = User.query.filter_by(email="admin@stayease.com").first()
    if not admin:
        admin = User(
            full_name="Resort Administrator",
            email="admin@stayease.com",
            contact_number="+63 (917) 123-4567",
            role="admin"
        )
        admin.set_password("Admin123!")
        db.session.add(admin)
        print("Demo admin user created: admin@stayease.com / Admin123!")

    # Seed Demo Customer
    customer = User.query.filter_by(email="customer@stayease.com").first()
    if not customer:
        customer = User(
            full_name="Maria Santos",
            email="customer@stayease.com",
            contact_number="+63 (918) 987-6543",
            role="customer"
        )
        customer.set_password("Customer123!")
        db.session.add(customer)
        print("Demo customer user created: customer@stayease.com / Customer123!")

    db.session.commit()

    # Seed Accommodations
    if AccommodationUnit.query.count() == 0:
        units = [
            AccommodationUnit(
                name="Sunset Ocean Villa", 
                description="Luxury private villa with direct beach access and infinity plunge pool.", 
                capacity=4, 
                nightly_rate=7500.00,
                image_url="https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80"
            ),
            AccommodationUnit(
                name="Palm Garden Cottage", 
                description="Spacious tropical cottage surrounded by lush garden flora.", 
                capacity=6, 
                nightly_rate=5500.00,
                image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80"
            ),
            AccommodationUnit(
                name="Beachfront Suite", 
                description="Romantic master suite featuring panoramic ocean views and private balcony.", 
                capacity=2, 
                nightly_rate=4200.00,
                image_url="https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=800&q=80"
            )
        ]
        db.session.add_all(units)
        db.session.commit()

        # Seed Interior & Feature Image Sets for each Cottage Choice Package
        from app.models import AccommodationImage
        
        u1 = units[0] # Sunset Ocean Villa
        u2 = units[1] # Palm Garden Cottage
        u3 = units[2] # Beachfront Suite

        images_u1 = [
            AccommodationImage(accommodation_unit_id=u1.id, image_url="https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80", title="Private Villa & Pool", caption="Infinity plunge pool overlooking the ocean beach.", is_interior=False, display_order=1),
            AccommodationImage(accommodation_unit_id=u1.id, image_url="https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80", title="Master Bedroom", caption="King-size bed with sea view and premium linens.", is_interior=True, display_order=2),
            AccommodationImage(accommodation_unit_id=u1.id, image_url="https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=800&q=80", title="Living & Lounge Space", caption="Air-conditioned lounge with smart TV and plush sofa.", is_interior=True, display_order=3),
            AccommodationImage(accommodation_unit_id=u1.id, image_url="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80", title="Luxury Ensuite Bathroom", caption="Marble soaking tub, rain shower, and double vanity.", is_interior=True, display_order=4),
            AccommodationImage(accommodation_unit_id=u1.id, image_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80", title="Private Sunset Deck", caption="Sun loungers and outdoor dining table.", is_interior=False, display_order=5),
        ]

        images_u2 = [
            AccommodationImage(accommodation_unit_id=u2.id, image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80", title="Garden Cottage Porch", caption="Lush tropical flora surrounding private porch.", is_interior=False, display_order=1),
            AccommodationImage(accommodation_unit_id=u2.id, image_url="https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?auto=format&fit=crop&w=800&q=80", title="Cottage Living Room", caption="Warm wooden interiors with comfortable family seating.", is_interior=True, display_order=2),
            AccommodationImage(accommodation_unit_id=u2.id, image_url="https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=800&q=80", title="Family Bedroom", caption="Multiple comfortable beds with air conditioning.", is_interior=True, display_order=3),
            AccommodationImage(accommodation_unit_id=u2.id, image_url="https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=800&q=80", title="Kitchenette & Dining", caption="Equipped with mini-fridge, microwave, and dining nook.", is_interior=True, display_order=4),
            AccommodationImage(accommodation_unit_id=u2.id, image_url="https://images.unsplash.com/photo-1507652313519-d4e9174996dd?auto=format&fit=crop&w=800&q=80", title="Ensuite Bathroom", caption="Clean modern bathroom with hot water shower.", is_interior=True, display_order=5),
        ]

        images_u3 = [
            AccommodationImage(accommodation_unit_id=u3.id, image_url="https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=800&q=80", title="Suite Balcony & Ocean View", caption="Panoramic views directly overlooking the beach.", is_interior=False, display_order=1),
            AccommodationImage(accommodation_unit_id=u3.id, image_url="https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80", title="Honeymoon Suite Bedroom", caption="Romantic king bed layout with ocean breeze.", is_interior=True, display_order=2),
            AccommodationImage(accommodation_unit_id=u3.id, image_url="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80", title="Rain Shower Bathroom", caption="Glass-enclosed rainfall shower with premium toiletries.", is_interior=True, display_order=3),
            AccommodationImage(accommodation_unit_id=u3.id, image_url="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80", title="Private Balcony Lounge", caption="Seating area for sunset cocktails.", is_interior=True, display_order=4),
        ]

        db.session.add_all(images_u1 + images_u2 + images_u3)
        db.session.commit()
        print("Demo accommodations and cottage interior image sets seeded.")

    # Seed Sample Booking Request if none exists
    if Booking.query.count() == 0 and customer and AccommodationUnit.query.first():
        unit = AccommodationUnit.query.first()
        from datetime import date, timedelta
        from app.services import BookingService, PaymentService
        
        d1 = date.today() + timedelta(days=7)
        d2 = date.today() + timedelta(days=10)
        
        booking, msg = BookingService.create_booking(
            customer_id=customer.id,
            accommodation_unit_id=unit.id,
            check_in=d1,
            check_out=d2,
            guest_count=2,
            special_requests="Honeymoon setup requested if possible."
        )
        if booking:
            BookingService.approve_booking(booking.id, admin.id)
            PaymentService.record_payment(
                booking_id=booking.id,
                amount=booking.total_price / 2,
                payment_method="GCash",
                payment_date=date.today(),
                recorded_by_id=admin.id,
                payment_reference="GCASH-DEMO-991"
            )
            print("Demo booking and payment seeded.")

    # Seed Gallery Items
    if GalleryItem.query.count() == 0:
        gallery_photos = [
            GalleryItem(title="Beachfront Sunset Villa", caption="Panoramic ocean views and private veranda.", image_url="https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=600&q=80", category="Villas", display_order=1),
            GalleryItem(title="Lagoon Infinity Pool", caption="Crystal clear waters overlooking tropical palm gardens.", image_url="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=600&q=80", category="Amenities", display_order=2),
            GalleryItem(title="Deluxe Cottage Suite", caption="Spacious king-size bedding with air conditioning and private bath.", image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=600&q=80", category="Cottages", display_order=3),
            GalleryItem(title="Family Ocean Bungalow", caption="Comfortably sleeps up to 8 guests with kitchen facilities.", image_url="https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&w=600&q=80", category="Cottages", display_order=4),
            GalleryItem(title="Private Beach Lounge", caption="Sun loungers and evening bonfire area.", image_url="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=600&q=80", category="Amenities", display_order=5),
            GalleryItem(title="Pristine Coastline", caption="Powder-white sand and calm swimming waters.", image_url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80", category="Beach", display_order=6)
        ]
        db.session.add_all(gallery_photos)
        db.session.commit()
        print("Demo gallery items seeded.")



if __name__ == "__main__":
    app.cli()
