"""Initialize database tables on Heroku"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import app, db

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

