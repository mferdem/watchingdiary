from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models import Watchlist, WatchlistItem
from datetime import datetime

watchlist_bp = Blueprint('watchlist', __name__, template_folder='templates', url_prefix='/watchlist')

# Tüm watchlist'leri sırayla göster
@watchlist_bp.route('/')
def index():
    lists = Watchlist.query.order_by(Watchlist.position.asc(), Watchlist.created_at.desc()).all()
    return render_template('watchlist.html', lists=lists)

# Yeni watchlist oluştur
@watchlist_bp.route('/new', methods=['POST'])
def create_watchlist():
    name = request.form.get('name')
    description = request.form.get('description')
    countdown_date_str = request.form.get('countdown_date') or None
    countdown_date = None
    if countdown_date_str:
        countdown_date = datetime.strptime(countdown_date_str, "%Y-%m-%d").date()
    position = Watchlist.query.count()
    wl = Watchlist(name=name, description=description, countdown_date=countdown_date, position=position)
    db.session.add(wl)
    db.session.commit()
    return redirect(url_for('watchlist.index'))

# Listelerin sırasını kaydet (drag-drop)
@watchlist_bp.route('/reorder_lists', methods=['POST'])
def reorder_lists():
    order = request.json.get('order')  # [list_id1, list_id2, ...]
    for pos, list_id in enumerate(order):
        wl = Watchlist.query.get(list_id)
        if wl:
            wl.position = pos
    db.session.commit()
    return jsonify({'success': True})

# Item ekle
@watchlist_bp.route('/<int:watchlist_id>/add_item', methods=['POST'])
def add_item(watchlist_id):
    wl = Watchlist.query.get_or_404(watchlist_id)
    name = request.form.get('name')
    if name:
        position = WatchlistItem.query.filter_by(watchlist_id=wl.id).count()
        item = WatchlistItem(watchlist_id=wl.id, name=name, position=position)
        db.session.add(item)
        db.session.commit()
    if request.is_json:
        return jsonify({'success': True})
    return redirect(url_for('watchlist.index'))

# Item sırası (drag-drop)
@watchlist_bp.route('/<int:watchlist_id>/reorder', methods=['POST'])
def reorder_items(watchlist_id):
    wl = Watchlist.query.get_or_404(watchlist_id)
    order = request.json.get('order')  # [item_id1, item_id2, ...]
    for pos, item_id in enumerate(order):
        item = WatchlistItem.query.get(item_id)
        if item and item.watchlist_id == wl.id:
            item.position = pos
    db.session.commit()
    return jsonify({'success': True})

# Item'ı sil
@watchlist_bp.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    item = WatchlistItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

# Tamamlandı toggle
@watchlist_bp.route('/item/<int:item_id>/toggle', methods=['POST'])
def toggle_item(item_id):
    item = WatchlistItem.query.get_or_404(item_id)
    item.completed = not item.completed
    db.session.commit()
    return jsonify({'success': True, 'completed': item.completed})