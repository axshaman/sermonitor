from flask import Flask
from models.models import db

def create_app():
    app = Flask(__name__)
    app.secret_key = ''

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://pashkan:password@deleteme_db:5432/deleteme'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)
    return app
