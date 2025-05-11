from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)

    # Film için
    year = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    imdb_id = db.Column(db.String(50))
    rating = db.Column(db.Float)
    filmincinema = db.Column(db.Boolean)

    # Dizi için
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)

    # Ortak alanlar
    location = db.Column(db.String(255))
    companions = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer, default=1)

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
