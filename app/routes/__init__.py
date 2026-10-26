from app.routes.public import public_bp
from app.routes.auth import auth_bp
from app.routes.customer import customer_bp
from app.routes.admin import admin_bp

__all__ = ['public_bp', 'auth_bp', 'customer_bp', 'admin_bp']
