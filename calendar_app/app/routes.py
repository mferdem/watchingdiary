from flask import Blueprint, render_template, request, redirect, url_for
from app.models import db, Log
from collections import defaultdict
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    logs = Log.query.order_by(Log.date.desc()).all()
    logs_by_date = defaultdict(list)
    for log in logs:
        logs_by_date[log.date].append(log)
    return render_template('index.html', logs_by_date=logs_by_date)

@main.route('/add_log', methods=['POST'])
def add_log():
    date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    activity_type = request.form['activity_type']
    description = request.form.get('description', '')
    location = request.form.get('location', '')
    rating = request.form.get('rating')
    rating = float(rating) if rating else None

    new_log = Log(date=date, activity_type=activity_type, description=description,
                  location=location, rating=rating)
    db.session.add(new_log)
    db.session.commit()
    return redirect(url_for('main.index'))
