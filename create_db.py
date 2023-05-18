from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sqcovnamegkmuj:7b7e16591935aa6b49d3c8735cd9db36aba0904359a4d7fa69c7b17894668406@ec2-3-217-146-37.compute-1.amazonaws.com:5432/dabcmiilq6u3t6'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True, server_default=db.text("nextval('subscriber_id_seq'::regclass)"))
    viber_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    avatar = db.Column(db.Text)
    country = db.Column(db.Text)
    language = db.Column(db.Text)
    api_version = db.Column(db.Integer)
    phone_number = db.Column(db.Text)

class SubscriberMessage(db.Model):
    viber_id = db.Column(db.Text, primary_key=True)
    message = db.Column(db.Text)

# Create the database tables
with app.app_context():
    db.create_all()