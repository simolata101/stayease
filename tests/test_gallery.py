import pytest
from app.models import GalleryItem, User, AccommodationUnit, AccommodationImage

def test_admin_gallery_maintenance(client, init_database):
    # Register and seed admin
    admin = User(full_name="Admin Test", email="admin_gallery@test.com", role="admin")
    admin.set_password("admin123")
    init_database.session.add(admin)
    init_database.session.commit()

    # Login as admin
    client.post('/auth/login', data=dict(
        email='admin_gallery@test.com',
        password='admin123'
    ), follow_redirects=True)

    # Add a new photo via /admin/gallery
    response = client.post('/admin/gallery', data=dict(
        title='New Ocean Infinity Deck',
        caption='Newly built ocean viewing deck.',
        image_url='https://images.unsplash.com/photo-1540555700478-4be289fbecef',
        category='Amenities',
        display_order=1
    ), follow_redirects=True)

    assert response.status_code == 200
    assert b'New Ocean Infinity Deck' in response.data

    # Verify item exists in database
    item = GalleryItem.query.filter_by(title='New Ocean Infinity Deck').first()
    assert item is not None
    assert item.is_active is True

    # Toggle visibility to hidden
    response = client.post(f'/admin/gallery/{item.id}/toggle', follow_redirects=True)
    assert response.status_code == 200
    assert item.is_active is False

    # Check public gallery does not show hidden items
    pub_response = client.get('/gallery')
    assert b'New Ocean Infinity Deck' not in pub_response.data


def test_admin_cottage_image_maintenance(client, init_database):
    # Seed admin & accommodation unit
    admin = User(full_name="Admin Cottage Test", email="admin_cottage@test.com", role="admin")
    admin.set_password("admin123")

    unit = AccommodationUnit(
        name="Test Lagoon Suite",
        description="Luxury suite",
        capacity=4,
        nightly_rate=5000.00,
        is_active=True
    )
    init_database.session.add(admin)
    init_database.session.add(unit)
    init_database.session.commit()

    # Login as admin
    client.post('/auth/login', data=dict(
        email='admin_cottage@test.com',
        password='admin123'
    ), follow_redirects=True)

    # Add cottage interior photo
    add_resp = client.post('/admin/gallery/cottage-image/add', data=dict(
        accommodation_unit_id=unit.id,
        title='Royal Master Bedroom',
        caption='King bed with jacuzzi view',
        image_url='https://images.unsplash.com/photo-1590490360182-c33d57733427',
        is_interior='1',
        display_order=1
    ), follow_redirects=True)

    assert add_resp.status_code == 200
    img = AccommodationImage.query.filter_by(title='Royal Master Bedroom').first()
    assert img is not None
    assert img.is_interior is True
    assert img.accommodation_unit_id == unit.id

    # Edit / Replace image URL and title
    edit_resp = client.post(f'/admin/gallery/cottage-image/{img.id}/edit', data=dict(
        title='Replaced Master Bedroom Photo',
        caption='Updated luxury bedding suite',
        image_url='https://images.unsplash.com/photo-1582719478250-c89cae4dc85b',
        is_interior='1'
    ), follow_redirects=True)

    assert edit_resp.status_code == 200
    db_img = init_database.session.get(AccommodationImage, img.id)
    assert db_img.title == 'Replaced Master Bedroom Photo'
    assert db_img.image_url == 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b'

    # Delete image
    del_resp = client.post(f'/admin/gallery/cottage-image/{img.id}/delete', follow_redirects=True)
    assert del_resp.status_code == 200
    assert init_database.session.get(AccommodationImage, img.id) is None
