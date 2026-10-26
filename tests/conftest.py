import pytest
import os
from app import create_app, db
from app.config import TestConfig
from app.models import User

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    admin = User(full_name='Admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    
    customer = User(full_name='Customer', email='customer@example.com', role='customer')
    customer.set_password('customer123')
    
    db.session.add(admin)
    db.session.add(customer)
    db.session.commit()
    
    return db
