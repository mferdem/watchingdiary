from flask import Blueprint, render_template, request
from app.models import Movie  # Projenizdeki import yoluna göre güncelleyin
from app import db
from app.models import db, Log, Movie, CinemaViewing


movies_bp = Blueprint('movies', __name__, template_folder='templates', url_prefix='/movies')

@movies_bp.route('/list')
def movie_list():
    year = request.args.get('year', type=int)
    decade = request.args.get('decade', type=int)

    movies_query = Movie.query

    if year:
        movies_query = movies_query.filter(Movie.year == year)
    elif decade:
        movies_query = movies_query.filter(Movie.year >= decade, Movie.year < decade + 10)

    movies = movies_query.order_by(Movie.id.desc()).all()

    enriched = []
    for movie in movies:
        logs = Log.query.filter_by(movie_id=movie.id, activity_type='movie', status=1).all()
        cinema_views = CinemaViewing.query.filter_by(movie_id=movie.id).count()
        last_watch = max((log.date for log in logs if log.date), default=None)

        enriched.append({
            'movie': movie,
            'watch_count': len(logs),
            'cinema_count': cinema_views,
            'last_watch': last_watch
        })

    return render_template(
        'movie_list.html',
        movies=enriched,
        selected_year=year,
        selected_decade=decade
    )

@movies_bp.route('/cinema')
def cinema_movies():
    from app.models import CinemaViewing

    viewings = CinemaViewing.query.order_by(CinemaViewing.date.desc()).all()

    return render_template('cinema_movies.html', entries=viewings)

@movies_bp.route('/year-distribution')
def movie_year_distribution():
    data = (
        db.session.query(Movie.year, db.func.count(Movie.id))
        .group_by(Movie.year)
        .order_by(Movie.year)
        .all()
    )
    years = [year for year, count in data if year is not None]
    counts = [count for year, count in data if year is not None]

    return render_template('movie_year_distribution.html', years=years, counts=counts)


@movies_bp.route('/watches-overview')
def watches_overview():
    from app.models import Log
    from sqlalchemy import func, extract

    # 1. Toplam izlenme (log bazlı)
    watch_data = (
        db.session.query(
            extract('year', Log.date).label('year'),
            func.count(Log.id).label('count')
        )
        .filter(Log.activity_type == 'movie')
        .group_by('year')
        .order_by('year')
        .all()
    )
    watch_years = [int(row.year) for row in watch_data]
    watch_counts = [row.count for row in watch_data]

    # 2. İlk izlenme (her film için en erken tarih)
    subquery = (
        db.session.query(
            Log.movie_id,
            func.min(Log.date).label('first_watch')
        )
        .filter(Log.activity_type == 'movie')
        .group_by(Log.movie_id)
        .subquery()
    )

    new_data = (
        db.session.query(
            extract('year', subquery.c.first_watch).label('year'),
            func.count().label('count')
        )
        .group_by('year')
        .order_by('year')
        .all()
    )
    new_years = [int(row.year) for row in new_data]
    new_counts = [row.count for row in new_data]

    return render_template(
        'movie_watches_overview.html',
        watch_years=watch_years,
        watch_counts=watch_counts,
        new_years=new_years,
        new_counts=new_counts
    )