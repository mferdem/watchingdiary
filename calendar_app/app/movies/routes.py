from flask import Blueprint, render_template, request, jsonify
from app.models import Movie  # Projenizdeki import yoluna göre güncelleyin
from app import db
from app.models import db, Log, Movie, CinemaViewing
from app.utils import measure_time


movies_bp = Blueprint('movies', __name__, template_folder='templates', url_prefix='/movies')

@movies_bp.route('/list')
def movie_list():
    # Bu sayfa sadece HTML şablonunu render eder
    year = request.args.get('year', type=int)
    decade = request.args.get('decade', type=int)

    return render_template(
        'movie_list.html',
        selected_year=year,
        selected_decade=decade
    )


@movies_bp.route('/data', methods=['POST'])
@measure_time
def movie_data():
    draw = int(request.form.get('draw', 1))
    start = int(request.form.get('start', 0))
    length = int(request.form.get('length', 10))
    search_value = request.form.get('search[value]', '')
    order_column_index = int(request.form.get('order[0][column]', 1))
    order_direction = request.form.get('order[0][dir]', 'asc')

    year = request.form.get('year', type=int)
    decade = request.form.get('decade', type=int)

    # Kolon sıralama haritası
    column_map = {
        0: Movie.id,
        1: Movie.year,
        2: Movie.name,
        3: Movie.duration,
    }

    # Ana sorgu
    query = db.session.query(Movie)

    if search_value:
        query = query.filter(Movie.name.ilike(f'%{search_value}%'))

    if year:
        query = query.filter(Movie.year == year)
    elif decade:
        query = query.filter(Movie.year >= decade, Movie.year < decade + 10)

    total_records = query.count()

    # Sıralama
    if order_column_index in column_map:
        column = column_map[order_column_index]
        if order_direction == 'desc':
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())
    else:
        query = query.order_by(Movie.id.desc())

    # Sayfalama
    movies = query.offset(start).limit(length).all()

    # Cevap datası
    data = []
    for idx, movie in enumerate(movies, start=start + 1):
        logs = Log.query.filter_by(movie_id=movie.id, activity_type='movie', status=1).all()
        cinema_count = CinemaViewing.query.filter_by(movie_id=movie.id).count()
        last_watch = max((log.date for log in logs if log.date), default=None)

        data.append({
            'index': idx,
            'year': movie.year,
            'title': f'<a href="https://www.imdb.com/title/{movie.imdb_id}" target="_blank" rel="noopener" class="text-decoration-none text-reset fw-bold">{movie.name}</a>'
                     if movie.imdb_id else movie.name,
            'duration': f"{movie.duration} min" if movie.duration else "-",
            'watch_count': len(logs),
            'cinema_count': cinema_count,
            'last_watch': last_watch.strftime('%d %b %Y') if last_watch else '-'
        })

    return jsonify({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': total_records,
        'data': data
    })

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