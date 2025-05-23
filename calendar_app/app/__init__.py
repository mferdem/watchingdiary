from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(testing=False):
    app = Flask(__name__)
    
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
    
    app.register_blueprint(movies_bp)
    app.register_blueprint(main_blueprint)

    return app
