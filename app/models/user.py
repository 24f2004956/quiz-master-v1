from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    qualification = db.Column(db.String(150))
    dob = db.Column(db.String(50))
    role = db.Column(db.String(10), nullable=False, default='user')
    
    scores = db.relationship('Score', backref='user', lazy=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        """Check password hash"""
        return check_password_hash(self.password, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'