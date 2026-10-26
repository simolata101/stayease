from app.models import User

def test_password_hashing():
    u = User(email='test@example.com')
    u.set_password('cat')
    assert not u.check_password('dog')
    assert u.check_password('cat')

def test_register(client, app):
    response = client.post('/auth/register', data=dict(
        full_name='New User',
        email='new@test.com',
        contact_number='123456789',
        password='password123',
        confirm_password='password123'
    ), follow_redirects=True)
    assert b'Registration successful' in response.data
    
    with app.app_context():
        assert User.query.count() == 1
        user = User.query.first()
        assert user.email == 'new@test.com'
        assert user.role == 'customer'

def test_register_duplicate_email(client, init_database):
    response = client.post('/auth/register', data=dict(
        full_name='Another User',
        email='customer@example.com', # already exists in init_database
        contact_number='123456789',
        password='password123',
        confirm_password='password123'
    ), follow_redirects=True)
    assert b'Email address already registered' in response.data

def test_login_logout(client, init_database):
    response = client.post('/auth/login', data=dict(
        email='customer@example.com',
        password='customer123'
    ), follow_redirects=True)
    assert b'My Reservation History' in response.data
    
    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert b'You have been logged out' in response.data

def test_login_invalid_password(client, init_database):
    response = client.post('/auth/login', data=dict(
        email='customer@example.com',
        password='wrongpassword'
    ), follow_redirects=True)
    assert b'Invalid email or password' in response.data
