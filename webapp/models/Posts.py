from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from webapp.db import get_db
db = get_db()
# db = SQLAlchemy()

class Posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    # author_id = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    created = db.Column(db.TIMESTAMP, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.Text, nullable=False)

    # Define foreign key relationship
    # author = db.relationship('Users', backref='posts')
    # Adding created_at and updated_at columns
    created_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow, onupdate=datetime.utcnow)
