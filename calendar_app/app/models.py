from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    location = db.Column(db.String(255))
    rating = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)
    rating = db.Column(db.Float)
