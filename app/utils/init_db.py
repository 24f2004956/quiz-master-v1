from werkzeug.security import generate_password_hash
from app.models.user import User
from app.extensions import db

def initialize_admin():
    """Initialize the admin user if it doesn't exist"""
    admin_email = "admin@quizmaster.com"  # Change this to your preferred admin email
    admin_password = "admin123"  # Change this to your preferred admin password
    
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        admin = User(
            email=admin_email,
            password=hashed_password,
            full_name="Admin User",
            qualification="System Administrator",
            dob="01-01-2000",
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
    else:
        print("Admin user already exists.")