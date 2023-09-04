from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(application)
migrate = Migrate(application, db)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True,)
    viber_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    avatar = db.Column(db.Text)
    country = db.Column(db.Text)
    language = db.Column(db.Text)
    api_version = db.Column(db.Integer)
    phone_number = db.Column(db.Text)

# Create the database tables
with application.app_context():
    db.create_all()