from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Log
from collections import defaultdict
from datetime import datetime, timedelta, date
from calendar import monthrange

main = Blueprint('main', __name__)

event_styles = {
    'film': {'size': 2},
    'dizi': {'size': 1},
    'maç': {'size': 2},
    'konser': {'size': 8},
    'randevu': {'size': 2},
    'hatırlatma': {'size': 2},
    'diğer': {'size': 2},
}


months_tr = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]


@main.route('/')
def index():
    # Ay ve yıl filtrelerini al (varsayılan: bugünkü ay)
    selected_year = int(request.args.get('year', datetime.today().year))
    selected_month = int(request.args.get('month', datetime.today().month))

    # Seçilen ayın günlerini oluştur
    num_days = monthrange(selected_year, selected_month)[1]
    days = [date(selected_year, selected_month, day) for day in range(1, num_days + 1)]

    # İlgili logları çek
    logs = Log.query.filter(
        Log.status == 1,
        Log.date.between(date(selected_year, selected_month, 1),
                        date(selected_year, selected_month, num_days))
    ).order_by(Log.date).all()

    # Günlük gruplama
    logs_by_date = defaultdict(list)
    for log in logs:
        logs_by_date[log.date].append(log)

    return render_template(
        'index.html',
        days = days,
        logs_by_date = logs_by_date,
        event_styles=event_styles,
        selected_year=selected_year,
        selected_month=selected_month,
        today=date.today(),
        months_tr=months_tr
    )



@main.route('/add_log', methods=['POST'])
def add_log():
    form = request.form
    activity_type = form['activity_type']
    date_value = datetime.strptime(form['date'], '%Y-%m-%d').date()

    # Ortak alanlar
    name = form.get('name', '').strip()
    notes = form.get('notes', '').strip()

    log = Log(
        date=date_value,
        activity_type=activity_type,
        name=name,
        notes=notes
    )

    # Film
    if activity_type == 'film':
        log.year = form.get('year') or None
        log.duration = form.get('duration') or None
        log.imdb_id = form.get('imdb_id') or None
        log.rating = float(form['rating']) if form.get('rating') else None
        log.filmincinema = form.get('filmInCinema') == 'on'
        if log.filmincinema:
            log.location = form.get('location_cinema') or None
            log.companions = form.get('companions_cinema') or None

    # Dizi
    elif activity_type == 'dizi':
        log.season = form.get('season') or None
        log.episode = form.get('episode') or None

    # Maç
    elif activity_type == 'maç':
        if form.get('matchInStadium') == 'on':
            log.location = form.get('location_match') or None
            log.companions = form.get('companions_match') or None

    # Konser
    elif activity_type == 'konser':
        log.location = form.get('location_concert') or None
        log.companions = form.get('companions_concert') or None

    db.session.add(log)
    db.session.commit()

    return redirect(url_for('main.index'))


@main.route('/delete_log/<int:log_id>', methods=['POST'])
def delete_log(log_id):
    log = Log.query.get_or_404(log_id)
    log.status = 0
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/edit_log/<int:log_id>', methods=['GET', 'POST'])
def edit_log(log_id):
    log = Log.query.get_or_404(log_id)

    if request.method == 'POST':
        form = request.form
        log.date = datetime.strptime(form['date'], '%Y-%m-%d').date()
        log.activity_type = form['activity_type']
        log.name = form.get('name', '').strip()
        log.notes = form.get('notes', '').strip()

        # Film
        if log.activity_type == 'film':
            log.year = form.get('year') or None
            log.duration = form.get('duration') or None
            log.imdb_id = form.get('imdb_id') or None
            log.rating = float(form['rating']) if form.get('rating') else None
            log.filmincinema = form.get('filmInCinema') == 'on'
            if log.filmincinema:
                log.location = form.get('location_film') or None
                log.companions = form.get('companions_film') or None

        # Dizi
        elif log.activity_type == 'dizi':
            log.season = form.get('season') or None
            log.episode = form.get('episode') or None

        # Maç
        elif log.activity_type == 'maç':
            log.location = form.get('location_match') or None if form.get('matchInStadium') == 'on' else None
            log.companions = form.get('companions_match') or None if form.get('matchInStadium') == 'on' else None

        # Konser
        elif log.activity_type == 'konser':
            log.location = form.get('location_concert') or None
            log.companions = form.get('companions_concert') or None

        db.session.commit()
        return redirect(url_for('main.index'))

    return render_template('edit_log.html', log=log, today=log.date, selected_type=log.activity_type)
