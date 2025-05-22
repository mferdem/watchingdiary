from flask import Blueprint, render_template, request, jsonify
from app.models import Movie  # Projenizdeki import yoluna göre güncelleyin
from app import db
from app.models import db, Log, Movie, CinemaViewing
from app.utils import measure_time
from sqlalchemy import func, desc, and_
from sqlalchemy.orm import aliased


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

    # Alias'lar
    log_alias = aliased(Log)
    cinema_alias = aliased(CinemaViewing)

    # Sorgu
    query = db.session.query(
        Movie,
        func.count(log_alias.id).label('watch_count'),
        func.count(cinema_alias.id).label('cinema_count'),
        func.max(log_alias.date).label('last_watch')
    ).outerjoin(log_alias, (log_alias.movie_id == Movie.id) & (log_alias.status == 1) & (log_alias.activity_type == 'movie')) \
     .outerjoin(cinema_alias, cinema_alias.movie_id == Movie.id) \
     .group_by(Movie.id)

    # Arama filtresi
    if search_value:
        query = query.filter(Movie.name.ilike(f'%{search_value}%'))

    # Yıl / on yıl filtreleri
    if year:
        query = query.filter(Movie.year == year)
    elif decade:
        query = query.filter(Movie.year >= decade, Movie.year < decade + 10)

    # Kolon sıralama haritası
    column_map = {
        0: Movie.id,
        1: Movie.year,
        2: Movie.name,
        3: Movie.duration,
        4: 'watch_count',
        5: 'cinema_count',
        6: 'last_watch'
    }

    # Sıralama uygulama
    col = column_map.get(order_column_index, Movie.id)
    if isinstance(col, str):  # türetilmiş alan
        query = query.order_by(desc(col)) if order_direction == 'desc' else query.order_by(col)
    else:  # doğrudan kolon
        query = query.order_by(col.desc() if order_direction == 'desc' else col.asc())

    total_records = query.count()
    rows = query.offset(start).limit(length).all()

    data = []
    for idx, row in enumerate(rows, start=start + 1):
        movie, watch_count, cinema_count, last_watch = row
        data.append({
            'index': idx,
            'year': movie.year,
            'title': f'<a href="https://www.imdb.com/title/{movie.imdb_id}" target="_blank" rel="noopener" class="text-decoration-none text-reset fw-bold">{movie.name}</a>'
                     if movie.imdb_id else movie.name,
            'duration': f"{movie.duration} min" if movie.duration else "-",
            'watch_count': watch_count,
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

@movies_bp.route('/movie-year-distribution')
def movie_year_distribution():
    raw_data = (
        db.session.query(Movie.year, db.func.count(Movie.id))
        .group_by(Movie.year)
        .order_by(Movie.year)
        .all()
    )

    year_counts = {year: count for year, count in raw_data if year is not None}

    min_year = min(year_counts.keys())
    max_year = max(year_counts.keys())

    years = list(range(min_year, max_year + 1))
    counts = [year_counts.get(year, 0) for year in years]

    return render_template('movie_year_distribution.html', years=years, counts=counts)


@movies_bp.route('/watch-year-distribution')
def watch_year_distribution():
    from app.models import Log
    from sqlalchemy import func, extract
    from datetime import datetime

    current_year = datetime.now().year
    today_day_of_year = datetime.now().timetuple().tm_yday
    total_days_in_year = 366 if (current_year % 4 == 0 and (current_year % 100 != 0 or current_year % 400 == 0)) else 365
    year_progress = today_day_of_year / total_days_in_year

    # 1. Toplam izlenme
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

    # 2. İlk izlenme
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

    # 3. Tahmin: sadece bu yıla ait olanları hesapla
    projected_watch = 0
    projected_new = 0

    if current_year in watch_years:
        current_count = watch_counts[watch_years.index(current_year)]
        projected_watch = round(current_count / year_progress)

    if current_year in new_years:
        current_new = new_counts[new_years.index(current_year)]
        projected_new = round(current_new / year_progress)

    return render_template(
        'watch_year_distribution.html',
        watch_years=watch_years,
        watch_counts=watch_counts,
        new_years=new_years,
        new_counts=new_counts,
        current_year=current_year,
        projected_watch=projected_watch,
        projected_new=projected_new
    )

@movies_bp.route('/grid')
def movie_grid():
    # Filtre parametrelerini al
    year = request.args.get('year', type=int)
    decade = request.args.get('decade', type=int)
    page = request.args.get('page', 1, type=int)
    return render_template('movie_grid.html',
                           selected_year=year,
                           selected_decade=decade,
                           selected_page=page)

@movies_bp.route('/grid/data')
def movie_grid_data():
    year = request.args.get('year', type=int)
    decade = request.args.get('decade', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = 36

    # Sorgu oluştur
    query = Movie.query
    if year:
        query = query.filter(Movie.year == year)
    elif decade:
        query = query.filter(and_(Movie.year >= decade, Movie.year < decade + 10))

    total = query.count()
    movies = query.order_by(Movie.year.desc()).offset((page - 1) * page_size).limit(page_size).all()

    results = []
    for m in movies:
        results.append({
            'name': m.name,
            'year': m.year,
            'imdb_id': m.imdb_id
        })

    return jsonify({
        'movies': results,
        'total': total,
        'page': page,
        'page_size': page_size
    })