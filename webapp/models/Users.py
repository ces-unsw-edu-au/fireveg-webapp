from flask_sqlalchemy import SQLAlchemy
from webapp.db import get_db
db = get_db()
from datetime import datetime


# db = SQLAlchemy()
from enum import Enum

class Role(Enum):
    viewer = 'viewer'
    downloader = 'downloader'

    def __str__(self):
        return self.value

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Enum(Role), default=Role.viewer)
    is_email_verified = db.Column(db.Boolean, default=False, index=True)
    email_verification_code = db.Column(db.String(255), index=True)
    # Define the one-to-many relationship with RoleUpgradeRequest
    # role_upgrade_requests = db.relationship('RoleUpgradeRequests', backref='user', lazy='dynamic')

    # Uncomment the following line to establish the one-to-many relationship
    role_upgrade_requests = db.relationship('RoleUpgradeRequests', backref='user', lazy='dynamic')

    # Uncomment the following line to establish the one-to-many relationship
    posts = db.relationship('Posts', backref='author', lazy='dynamic')
    
    # Adding created_at and updated_at columns
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __getitem__(self, key):
        return self.__dict__[key]
