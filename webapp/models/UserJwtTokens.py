from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from webapp.db import get_db
db = get_db()
# db = SQLAlchemy()

class UserJwtTokens(db.Model):
    __tablename__ = "user_jwt_tokens"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    token = db.Column(db.String(500), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
