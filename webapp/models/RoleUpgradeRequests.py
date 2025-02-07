from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from webapp.db import get_db
db = get_db()

class RoleUpgradeRequests(db.Model):
    __tablename__ = "role_upgrade_requests"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String, nullable=False)
    
    # Define the foreign key relationship with User
    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Uncomment the following line to establish the many-to-one relationship
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Adding created_at and updated_at columns
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)