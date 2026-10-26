import pytest
from app.models import GalleryItem, User

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
