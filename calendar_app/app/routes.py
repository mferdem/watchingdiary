from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from calendar import monthrange
from app.models import db, Log, Movie, Series
import csv
import io
from imdb import IMDb

main = Blueprint('main', __name__)

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
        months_tr=["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                   "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    )

@main.route('/add_log', methods=['POST'])
def add_log():
    form = request.form
    activity_type = form['activity_type']
    date_value = datetime.strptime(form['date'], '%Y-%m-%d').date()

    name = form.get('name', '').strip()
    notes = form.get('notes', '').strip()

    log = Log(
        date=date_value,
        activity_type=activity_type,
        name=name,
        notes=notes
    )

    if activity_type == 'movie':
        log.year = form.get('year') or None
        log.duration = form.get('duration') or None
        log.imdb_id = form.get('imdb_id') or None
        log.rating = float(form['rating']) if form.get('rating') else None
        log.filmincinema = form.get('filmInCinema') == 'on'
        if log.filmincinema:
            log.location = form.get('location_cinema') or None
            log.companions = form.get('companions_cinema') or None

        existing_movie = None
        if log.imdb_id:
            existing_movie = Movie.query.filter_by(imdb_id=log.imdb_id).first()
        else:
            existing_movie = Movie.query.filter_by(name=name, year=log.year).first()

        if not existing_movie:
            new_movie = Movie(
                name=name,
                year=log.year,
                duration=log.duration,
                imdb_id=log.imdb_id
            )
            db.session.add(new_movie)

    elif activity_type == 'series':
        log.season = form.get('season') or None
        log.episode = form.get('episode') or None

        existing_series = None
        if log.imdb_id:
            existing_series = Series.query.filter_by(imdb_id=log.imdb_id).first()
        else:
            existing_series = Series.query.filter_by(name=name).first()

        if not existing_series:
            new_series = Series(
                name=name,
                imdb_id=log.imdb_id,
                start_year=None,
                end_year=None
            )
            db.session.add(new_series)

    elif activity_type == 'match':
        if form.get('matchInStadium') == 'on':
            log.location = form.get('location_match') or None
            log.companions = form.get('companions_match') or None

    elif activity_type == 'concert':
        log.location = form.get('location_concert') or None
        log.companions = form.get('companions_concert') or None

    db.session.add(log)
    db.session.commit()

    return redirect(url_for('main.index'))

@main.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
def edit_log(log_id):
    log = Log.query.get_or_404(log_id)

    if request.method == 'POST':
        log.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        log.activity_type = request.form['activity_type']
        log.name = request.form['name']
        log.notes = request.form.get('notes')

        if log.activity_type == 'movie':
            log.year = request.form.get('year') or None
            log.duration = request.form.get('duration') or None
            log.imdb_id = request.form.get('imdb_id') or None
            log.rating = float(request.form['rating']) if request.form.get('rating') else None
            log.filmincinema = request.form.get('filmInCinema') == 'on'
            if log.filmincinema:
                log.location = request.form.get('location_cinema') or None
                log.companions = request.form.get('companions_cinema') or None
            else:
                log.location = None
                log.companions = None

        elif log.activity_type == 'series':
            log.season = request.form.get('season') or None
            log.episode = request.form.get('episode') or None

        elif log.activity_type == 'match':
            if request.form.get('matchInStadium') == 'on':
                log.location = request.form.get('location_match') or None
                log.companions = request.form.get('companions_match') or None
            else:
                log.location = None
                log.companions = None

        elif log.activity_type == 'concert':
            log.location = request.form.get('location_concert') or None
            log.companions = request.form.get('companions_concert') or None

        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('edit_log.html', log=log)

@main.route('/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    log = Log.query.get_or_404(log_id)
    log.status = 0
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/movies')
def movie_list():
    from app.models import Movie, Log
    year = request.args.get('year', type=int)

    movies_query = Movie.query
    if year:
        movies_query = movies_query.filter(Movie.year == year)

    movies = movies_query.order_by(Movie.year.desc().nullslast(), Movie.name.asc()).all()

    enriched_movies = []
    for movie in movies:
        logs = Log.query.filter_by(activity_type='movie', name=movie.name, status=1).all()
        watch_count = len(logs)
        cinema_count = sum(1 for log in logs if log.filmincinema)
        last_watch = max((log.date for log in logs if log.date), default=None)

        enriched_movies.append({
            'movie': movie,
            'watch_count': watch_count,
            'cinema_count': cinema_count,
            'last_watch': last_watch
        })

    return render_template(
        'movie_list.html',
        movies=enriched_movies,
        selected_year=year
    )

@main.route('/import_logs', methods=['GET', 'POST'])
def import_logs():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(request.url)

        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            flash('Unable to decode CSV file. Make sure it is UTF-8 encoded.', 'danger')
            return redirect(request.url)

        reader = csv.DictReader(io.StringIO(content))
        imported_count = 0
        skipped = 0

        for row in reader:
            try:
                date_value = datetime.strptime(row['date'], '%Y-%m-%d').date()
                activity_type = row['activity_type'].strip().lower()
                name = row.get('name', '').strip()

                if not activity_type or not name:
                    skipped += 1
                    continue

                log = Log(
                    date=date_value,
                    activity_type=activity_type,
                    name=name,
                    notes=row.get('notes', '').strip(),
                    year=int(row['year']) if row.get('year') else None,
                    duration=int(row['duration']) if row.get('duration') else None,
                    imdb_id=row.get('imdb_id') or None,
                    rating=float(row['rating']) if row.get('rating') else None,
                    filmincinema=row.get('filmincinema', '').lower() == 'yes',
                    season=int(row['season']) if row.get('season') else None,
                    episode=int(row['episode']) if row.get('episode') else None,
                    location=row.get('location') or None,
                    companions=row.get('companions') or None,
                    status=1
                )

                db.session.add(log)

                if activity_type == 'movie':
                    existing = Movie.query.filter_by(name=name, year=log.year).first()
                    if not existing:
                        db.session.add(Movie(
                            name=name,
                            year=log.year,
                            duration=log.duration,
                            imdb_id=log.imdb_id,
                            rating=log.rating
                        ))

                if activity_type == 'series':
                    existing = Series.query.filter_by(name=name).first()
                    if not existing:
                        db.session.add(Series(name=name))

                imported_count += 1

            except Exception as e:
                print(f"Skipping row due to error: {e}")
                skipped += 1

        db.session.commit()
        flash(f'{imported_count} logs imported. {skipped} skipped.', 'success')
        return redirect(url_for('main.index'))

    return render_template('import_logs.html')

@main.route('/import_movies_csv', methods=['GET', 'POST'])
def import_movies_csv():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename.endswith('.csv'):
            flash("Please upload a valid CSV file.", 'danger')
            return redirect(request.url)

        content = file.read().decode('utf-8')
        reader = csv.reader(io.StringIO(content), delimiter=';')

        imdb_api = IMDb()
        imported = 0
        skipped = 0
        next(reader)  # skip header row

        for row in reader:
            try:
                imdb_id = row[1].strip()
                if not imdb_id.startswith('tt'):
                    skipped += 1
                    continue

                # Movie bilgisi IMDb'den çekilir
                movie_info = imdb_api.get_movie(imdb_id[2:])
                title = movie_info.get('original title') or movie_info.get('title')
                year = movie_info.get('year')
                runtime = int(movie_info.get('runtimes', ['0'])[0])
                alt_name = movie_info.get('title')

                # Movie ekle (daha önce yoksa)
                existing = Movie.query.filter_by(name=title, year=year).first()
                if not existing:
                    movie = Movie(
                        name=title,
                        year=year,
                        duration=runtime,
                        imdb_id=imdb_id,
                    )
                    db.session.add(movie)
                else:
                    movie = existing

                # İzlenme tarihlerini işle
                for date_str in row[2:]:
                    date_str = date_str.strip()
                    if not date_str:
                        continue
                    try:
                        watch_date = datetime.strptime(date_str, '%d.%m.%Y').date()
                        log = Log(
                            date=watch_date,
                            activity_type='movie',
                            name=title,
                            notes=alt_name,
                            year=year,
                            duration=runtime,
                            imdb_id=imdb_id,
                            filmincinema=False,
                            status=1
                        )
                        db.session.add(log)
                    except Exception as e:
                        print(f"Invalid date format: {date_str} – {e}")
                        continue

                imported += 1
                print(f"{title} Added Succesfully")
            except Exception as e:
                print(f"Skipped row due to error: {e}")
                skipped += 1

        db.session.commit()
        flash(f"{imported} movie rows processed. {skipped} skipped.", 'success')
        return redirect(url_for('main.index'))

    return render_template('import_movies_csv.html')