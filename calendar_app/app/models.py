from datetime import datetime
from app import db

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)

    # Movie-specific
    year = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    imdb_id = db.Column(db.String(50))
    rating = db.Column(db.Float)
    filmincinema = db.Column(db.Boolean)

    # Series-specific
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)

    # Shared
    location = db.Column(db.String(255))
    companions = db.Column(db.String(255))

    status = db.Column(db.Integer, default=1)  # 1 = active, 0 = deleted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    imdb_id = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f"<Movie {self.name} ({self.year})>"

class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    imdb_id = db.Column(db.String(50), unique=True)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)

    def __repr__(self):
        return f"<Series {self.name} ({self.start_year}-{self.end_year or ''})>"
