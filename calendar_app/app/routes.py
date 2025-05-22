from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from calendar import monthrange
from app.models import db, Log, Movie, Series, CinemaViewing
from imdb import IMDb

main = Blueprint('main', __name__)

activity_sizes = {
    'movie': 4,
    'series': 3,
    'match': 6,
    'concert': 6,
    'appointment': 8,
    'reminder': 4,
    'other': 4
}

@main.route('/')
def index():
    today = date.today()
    selected_year = request.args.get('year', today.year, type=int)
    selected_month = request.args.get('month', today.month, type=int)
    num_days = monthrange(selected_year, selected_month)[1]
    days = [date(selected_year, selected_month, d) for d in range(1, num_days + 1)]

    logs = Log.query.filter(
        Log.status == 1,
        Log.date.between(date(selected_year, selected_month, 1),
                         date(selected_year, selected_month, num_days))
    ).order_by(Log.date).all()

    logs_by_date = {}
    for log in logs:
        logs_by_date.setdefault(log.date, []).append(log)

    return render_template(
        'index.html',
        days=days,
        logs_by_date=logs_by_date,
        selected_year=selected_year,
        selected_month=selected_month,
        today=today,
        activity_sizes=activity_sizes,
        months_tr=[
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
    )

@main.route('/add_log', methods=['POST'])
def add_log():
    form = request.form
    activity_type = form['activity_type']
    date_value = datetime.strptime(form['date'], '%Y-%m-%d').date()

    log = Log(
        date=date_value,
        activity_type=activity_type,
        name=form.get('name', '').strip(),
        notes=form.get('notes', '').strip()
    )

    if activity_type == 'movie':
        imdb_id = form.get('imdb_id') or None
        duration = form.get('duration') or None
        year = form.get('year') or None

        movie = Movie.query.filter_by(imdb_id=imdb_id).first() if imdb_id else Movie.query.filter_by(name=log.name, year=year).first()
        if not movie:
            movie = Movie(name=log.name, year=year, duration=duration, imdb_id=imdb_id)
            db.session.add(movie)
            db.session.flush()

        log.movie_id = movie.id

        if form.get('filmInCinema') == 'on':
            cinema = CinemaViewing(
                movie_id=movie.id,
                log=log,
                date=log.date,
                location=form.get('location_cinema'),
                companions=form.get('companions_cinema'),
                technology=form.get('cinema_tech') or None
            )
            db.session.add(cinema)

    elif activity_type == 'series':
        imdb_id = form.get('imdb_id') or None
        season = form.get('season')
        episode = form.get('episode')

        series = Series.query.filter_by(imdb_id=imdb_id).first() if imdb_id else Series.query.filter_by(name=log.name).first()
        if not series:
            series = Series(name=log.name, imdb_id=imdb_id)
            db.session.add(series)
            db.session.flush()

        log.series_id = series.id
        log.season = season
        log.episode = episode

    elif activity_type == 'match':
        if form.get('matchInStadium') == 'on':
            log.location = form.get('location_match')
            log.companions = form.get('companions_match')

    elif activity_type == 'concert':
        log.location = form.get('location_concert')
        log.companions = form.get('companions_concert')

    db.session.add(log)
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
def edit_log(log_id):
    log = Log.query.get_or_404(log_id)

    if request.method == 'POST':
        log.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        log.notes = request.form.get('notes', '').strip()
        activity_type = log.activity_type
        name = request.form.get('name', '').strip()
        imdb_id = request.form.get('imdb_id') or None

        log.location = None
        log.companions = None
        log.movie_id = None
        log.series_id = None
        log.season = None
        log.episode = None

        if activity_type == 'movie':
            year = request.form.get('year')
            duration = request.form.get('duration')
            in_cinema = request.form.get('filmInCinema') == 'on'

            movie = Movie.query.filter_by(imdb_id=imdb_id).first() if imdb_id else Movie.query.filter_by(name=name, year=year).first()
            if not movie:
                movie = Movie(name=name, year=year, duration=duration, imdb_id=imdb_id)
                db.session.add(movie)
                db.session.flush()

            log.movie_id = movie.id
            log.name = name

            CinemaViewing.query.filter_by(log_id=log.id).delete()

            if in_cinema:
                cinema = CinemaViewing(
                    movie_id=movie.id,
                    log=log,
                    date=log.date,
                    location=request.form.get('location_cinema'),
                    companions=request.form.get('companions_cinema'),
                    technology=request.form.get('cinema_tech') or None
                )
                db.session.add(cinema)

        elif activity_type == 'series':
            season = request.form.get('season')
            episode = request.form.get('episode')

            series = Series.query.filter_by(imdb_id=imdb_id).first() if imdb_id else Series.query.filter_by(name=name).first()
            if not series:
                series = Series(name=name, imdb_id=imdb_id)
                db.session.add(series)
                db.session.flush()

            log.series_id = series.id
            log.season = season
            log.episode = episode
            log.name = name

        elif activity_type == 'match':
            if request.form.get('matchInStadium') == 'on':
                log.location = request.form.get('location_match')
                log.companions = request.form.get('companions_match')
            log.name = name

        elif activity_type == 'concert':
            log.location = request.form.get('location_concert')
            log.companions = request.form.get('companions_concert')
            log.name = name

        else:
            log.name = name

        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('edit_log.html', log=log)

@main.route('/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    log = Log.query.get_or_404(log_id)
    log.status = 0
    db.session.commit()
    return redirect(url_for('main.index'))