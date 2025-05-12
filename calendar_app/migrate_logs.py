from app import create_app, db
from app.models import Log, Movie, Series
from sqlalchemy import or_

def migrate_logs():
    app = create_app()

    with app.app_context():
        logs = Log.query.filter(or_(
            Log.activity_type == 'movie',
            Log.activity_type == 'series'
        )).all()

        created_movies = 0
        created_series = 0
        updated_logs = 0

        for log in logs:
            if log.activity_type == 'movie':
                if log.movie_id:
                    continue

                movie = None
                if log.imdb_id:
                    movie = Movie.query.filter_by(imdb_id=log.imdb_id).first()
                if not movie:
                    movie = Movie.query.filter_by(name=log.name, year=log.year).first()

                if not movie:
                    movie = Movie(
                        name=log.name,
                        year=log.year,
                        duration=log.duration,
                        imdb_id=log.imdb_id or None
                    )
                    db.session.add(movie)
                    db.session.flush()
                    created_movies += 1

                log.movie_id = movie.id
                updated_logs += 1

            elif log.activity_type == 'series':
                if log.series_id:
                    continue

                series = Series.query.filter_by(name=log.name).first()
                if not series:
                    series = Series(name=log.name)
                    db.session.add(series)
                    db.session.flush()
                    created_series += 1

                log.series_id = series.id
                updated_logs += 1

        db.session.commit()

        print(f"✅ {updated_logs} logs updated.")
        print(f"🎬 {created_movies} movies created.")
        print(f"📺 {created_series} series created.")

if __name__ == '__main__':
    migrate_logs()
