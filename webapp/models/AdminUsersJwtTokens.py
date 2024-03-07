from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from webapp.db import get_db
db = get_db()
# db = SQLAlchemy()

class AdminUsersJwtTokens(db.Model):
    __tablename__ = "admin_users_jwt_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admin_users.id'), nullable=False, index=True)
    token = db.Column(db.String(500), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
