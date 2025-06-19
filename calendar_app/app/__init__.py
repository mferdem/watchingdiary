from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.filters import color_for_name

db = SQLAlchemy()
migrate = Migrate()

def create_app(testing=False):
    app = Flask(__name__)

    app.jinja_env.filters['color_for_name'] = color_for_name
    
    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Form testlerinde sorun yaşamamak için

    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'

    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    from app import models
    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main as main_blueprint
    from .movies import movies_bp
    from .series import series_bp
    from .watchlist import watchlist_bp
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(movies_bp)
    app.register_blueprint(series_bp)
    app.register_blueprint(watchlist_bp)

    return app
