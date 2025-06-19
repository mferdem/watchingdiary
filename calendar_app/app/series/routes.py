from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import db, Series, Season, Episode
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload

series_bp = Blueprint('series', __name__, template_folder='templates', url_prefix='/series')


@series_bp.route('/list')
def series_list():
    query = Series.query.options(
        joinedload(Series.seasons).joinedload(Season.episodes)
    )

    search = request.args.get('search')
    if search:
        query = query.filter(Series.name.ilike(f"%{search}%"))

    series_list = query.all()

    return render_template('series_list.html', series_list=series_list)


@series_bp.route('/new', methods=['GET', 'POST'])
def series_new():
    if request.method == 'POST':
        name = request.form.get('name')
        imdb_id = request.form.get('imdb_id')
        start_year = request.form.get('start_year', type=int)
        end_year = request.form.get('end_year', type=int)
        episode_duration = request.form.get('episode_duration', type=int)
        season_count = request.form.get('season_count', type=int)

        series = Series(
            name=name,
            imdb_id=imdb_id,
            start_year=start_year,
            end_year=end_year,
            episode_duration=episode_duration
        )
        db.session.add(series)
        db.session.flush()

        for i in range(1, season_count + 1):
            episode_count = request.form.get(f'season_{i}_episode_count', type=int)
            season = Season(series_id=series.id, season_number=i, episode_count=episode_count)
            db.session.add(season)
            db.session.flush()

            for j in range(1, episode_count + 1):
                episode = Episode(season_id=season.id, episode_number=j)
                db.session.add(episode)

        db.session.commit()
        flash('Series and seasons added successfully!', 'success')
        return redirect(url_for('series.series_list'))

    return render_template('series_new.html')

@series_bp.route('/<int:series_id>/detail', methods=['GET', 'POST'])
def series_detail(series_id):
    series = Series.query.get_or_404(series_id)

    if request.method == 'POST':
        watched_episodes = request.form.getlist('watched')
        for episode in series_episodes(series):
            episode.is_watched = str(episode.id) in watched_episodes
        db.session.commit()
        flash('Watched episodes updated!', 'success')
        return redirect(url_for('series.series_detail', series_id=series.id))

    return render_template('series_detail.html', series=series)

def series_episodes(series):
    return Episode.query.join(Season).filter(Season.series_id == series.id).all()

@series_bp.route('/stats')
def series_stats():
    series_data = db.session.query(
        Series,
        func.count(Episode.id).label('total'),
        func.sum(case((Episode.is_watched == True, 1), else_=0)).label('watched')
    ).select_from(Series) \
     .outerjoin(Season, Season.series_id == Series.id) \
     .outerjoin(Episode, Episode.season_id == Season.id) \
     .group_by(Series.id) \
     .all()

    return render_template('series_stats.html', series_data=series_data)

@series_bp.route('/<int:series_id>/edit', methods=['GET', 'POST'])
def series_edit(series_id):
    series = Series.query.get_or_404(series_id)

    if request.method == 'POST':
        # Ana dizi bilgileri
        series.name = request.form.get('name', '').strip()
        series.imdb_id = request.form.get('imdb_id', '').strip()
        series.start_year = request.form.get('start_year', type=int)
        series.end_year = request.form.get('end_year', type=int)
        series.episode_duration = request.form.get('episode_duration', type=int)

        # Sezon güncellemesi
        new_season_count = request.form.get('season_count', type=int)
        existing_seasons = {s.season_number: s for s in series.seasons}

        for i in range(1, new_season_count + 1):
            episode_count = request.form.get(f'season_{i}_episode_count', type=int)
            if i in existing_seasons:
                season = existing_seasons[i]
                if season.episode_count != episode_count:
                    # Bölüm sayısı değiştiyse, bölümleri güncelle
                    Episode.query.filter_by(season_id=season.id).delete()
                    db.session.flush()
                    for j in range(1, episode_count + 1):
                        episode = Episode(season_id=season.id, episode_number=j)
                        db.session.add(episode)
                    season.episode_count = episode_count
            else:
                # Yeni sezon ekleniyor
                season = Season(series_id=series.id, season_number=i, episode_count=episode_count)
                db.session.add(season)
                db.session.flush()
                for j in range(1, episode_count + 1):
                    episode = Episode(season_id=season.id, episode_number=j)
                    db.session.add(episode)

        # Fazladan kalmış sezon varsa sil
        for snum in sorted(existing_seasons.keys()):
            if snum > new_season_count:
                s = existing_seasons[snum]
                db.session.delete(s)

        db.session.commit()
        flash("Series updated successfully!", "success")
        return redirect(url_for('series.series_list'))

    return render_template('series_edit.html', series=series)