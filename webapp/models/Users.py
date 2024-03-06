from flask_sqlalchemy import SQLAlchemy
from webapp.db import get_db
db = get_db()
from datetime import datetime


# db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    
    # Define the one-to-many relationship with RoleUpgradeRequest
    # role_upgrade_requests = db.relationship('RoleUpgradeRequests', backref='user', lazy='dynamic')

    # Uncomment the following line to establish the one-to-many relationship
    role_upgrade_requests = db.relationship('RoleUpgradeRequests', backref='user', lazy='dynamic')

    # Uncomment the following line to establish the one-to-many relationship
    posts = db.relationship('Posts', backref='author', lazy='dynamic')
    
    # Adding created_at and updated_at columns
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
