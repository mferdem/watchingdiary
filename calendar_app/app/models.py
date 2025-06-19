from datetime import datetime
from app import db

# === Log ===
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
    concert_id = db.Column(db.Integer, db.ForeignKey('concert.id', name='fk_log_concert_id'))
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id', name='fk_log_episode_id'))

    location = db.Column(db.String(255))
    companions = db.Column(db.String(255))

    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movie = db.relationship("Movie", backref="logs")
    concert = db.relationship("Concert", backref="logs")
    episode = db.relationship("Episode", backref="logs")

    def is_movie(self):
        return self.activity_type == 'movie' and self.movie is not None

    def is_series(self):
        return self.activity_type == 'series' and self.episode is not None

    def is_concert(self):
        return self.activity_type == 'concert' and self.concert is not None

    def __repr__(self):
        return f"<Log {self.activity_type} on {self.date}>"

# === Movie ===
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

# === Series ===
class Series(db.Model):
    __tablename__ = 'series'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    imdb_id = db.Column(db.String(50), unique=True)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    episode_duration = db.Column(db.Integer)  # Ortalama bölüm süresi (dakika)

    def __repr__(self):
        return f"<Series {self.name} ({self.start_year}-{self.end_year or ''})>"

# === Season ===
class Season(db.Model):
    __tablename__ = 'season'

    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id', name='fk_season_series_id'), nullable=False)
    season_number = db.Column(db.Integer, nullable=False)
    episode_count = db.Column(db.Integer)

    series = db.relationship("Series", backref="seasons")

    def __repr__(self):
        return f"<Season S{self.season_number} of {self.series.name}>"

# === Episode ===
class Episode(db.Model):
    __tablename__ = 'episode'

    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id', name='fk_episode_season_id'), nullable=False)
    episode_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    air_date = db.Column(db.Date)
    is_watched = db.Column(db.Boolean, default=False)

    season = db.relationship("Season", backref="episodes")

    def __repr__(self):
        return f"<Episode S{self.season.season_number}E{self.episode_number} - {self.title}>"

# === Cinema Viewing ===
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

# === Concert ===
class Concert(db.Model):
    __tablename__ = 'concert'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    notes = db.Column(db.Text)

    def __repr__(self):
        return f"<Concert {self.name} at {self.location}>"

# === Watchlist ===
class Watchlist(db.Model):
    __tablename__ = 'watchlist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    countdown_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.Column(db.Integer, default=0)

    items = db.relationship('WatchlistItem', backref='watchlist', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Watchlist {self.name}>"

# === WatchlistItem ===
class WatchlistItem(db.Model):
    __tablename__ = 'watchlist_item'

    id = db.Column(db.Integer, primary_key=True)
    watchlist_id = db.Column(db.Integer, db.ForeignKey('watchlist.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.String(255))
    position = db.Column(db.Integer, nullable=False, default=0)
    completed = db.Column(db.Boolean, default=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<WatchlistItem {self.name}>"