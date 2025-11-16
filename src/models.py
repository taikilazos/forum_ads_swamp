"""
Database models for the SaaS app.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication and subscription management."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Subscription fields
    subscription_tier = db.Column(db.String(20), default='none')  # 'none', 'basic', 'pro', 'premium'
    subscription_active = db.Column(db.Boolean, default=False)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    
    # Drawing feature
    drawings_count = db.Column(db.Integer, default=0)
    
    # Relationship to drawings
    drawings = db.relationship('Drawing', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def can_draw(self):
        """Check if user can create a new drawing."""
        if self.subscription_active:
            return True  # Paid users get unlimited
        return self.drawings_count < 1  # Free users get 1 drawing


class Drawing(db.Model):
    """Drawing model to store user drawings."""
    __tablename__ = 'drawings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_data = db.Column(db.Text, nullable=False)  # Base64 encoded PNG
    message = db.Column(db.String(500), nullable=True)  # Optional message from user
    has_background = db.Column(db.Boolean, default=True)  # Whether drawing has white background
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_email = db.Column(db.String(120), nullable=False)  # Denormalized for easy display
    
    def __repr__(self):
        return f'<Drawing {self.id} by {self.user_email}>'

