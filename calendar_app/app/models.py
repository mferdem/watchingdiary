from datetime import datetime
from app import db

class Log(db.Model):
    __tablename__ = 'log'
    __table_args__ = (
        db.Index('ix_log_date', 'date'),
    )

    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(255))  # only for non-movie/series
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)

    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id', name='fk_log_movie_id'))
    series_id = db.Column(db.Integer, db.ForeignKey('series.id', name='fk_log_series_id'))
    concert_id = db.Column(db.Integer, db.ForeignKey('concert.id', name='fk_log_concert_id'))

    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)

    location = db.Column(db.String(255))
    companions = db.Column(db.String(255))

    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movie = db.relationship("Movie", backref="logs")
    series = db.relationship("Series", backref="logs")
    concert = db.relationship("Concert", backref="logs")

    def is_movie(self):
        return self.activity_type == 'movie' and self.movie is not None

    def is_series(self):
        return self.activity_type == 'series' and self.series is not None

    def is_concert(self):
        return self.activity_type == 'concert' and self.concert is not None

    def __repr__(self):
        return f"<Log {self.activity_type} on {self.date}>"

class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    imdb_id = db.Column(db.String(50), unique=True)
    my_rating = db.Column(db.Integer)
    tag = db.Column(db.String(255))

    def __repr__(self):
        return f"<Movie {self.name} ({self.year})>"

class Series(db.Model):
    __tablename__ = 'series'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    imdb_id = db.Column(db.String(50), unique=True)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)

    def __repr__(self):
        return f"<Series {self.name} ({self.start_year}-{self.end_year or ''})>"

class CinemaViewing(db.Model):
    __tablename__ = 'cinema_viewing'

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    log_id = db.Column(db.Integer, db.ForeignKey('log.id'), nullable=True)

    date = db.Column(db.Date)
    location = db.Column(db.String(255))
    companions = db.Column(db.String(255))
    technology = db.Column(db.String(50))  # e.g. IMAX, 3D

    movie = db.relationship("Movie", backref="cinema_viewings")
    log = db.relationship("Log", backref="cinema_viewing", uselist=False)

    def __repr__(self):
        return f"<CinemaViewing {self.movie.name} on {self.date}>"

class Concert(db.Model):
    __tablename__ = 'concert'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Concert {self.name} at {self.location}>"