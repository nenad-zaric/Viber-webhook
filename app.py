from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sqcovnamegkmuj:7b7e16591935aa6b49d3c8735cd9db36aba0904359a4d7fa69c7b17894668406@ec2-3-217-146-37.compute-1.amazonaws.com:5432/dabcmiilq6u3t6'
db = SQLAlchemy(app)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    viber_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    avatar = db.Column(db.Text)
    country = db.Column(db.Text)
    language = db.Column(db.Text)
    api_version = db.Column(db.Integer)
    member_id = db.Column(db.Text)

class SubscriberMessage(db.Model):
    viber_id = db.Column(db.Text, primary_key=True)
    message = db.Column(db.Text)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if data['event'] == 'message':
        viber_id = data['sender']['id']
        message_text = data['message'].get('text', '')

        if get_subscriber_message(viber_id) == '':
            store_subscriber_message(viber_id, message_text)

    if data['event'] == 'subscribed':
        create_subscriber(data)

    elif data['event'] == 'unsubscribed':
        delete_subscriber(data)

    return '', 200

@app.route('/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = db.session.query(Subscriber).all()
    subscriber_list = []

    for subscriber in subscribers:
        subscriber_data = {
            'id': subscriber.id,
            'viber_id': subscriber.viber_id,
            'name': subscriber.name,
            'avatar': subscriber.avatar,
            'country': subscriber.country,
            'language': subscriber.language,
            'api_version': subscriber.api_version,
            'member_id': subscriber.member_id
        }
        subscriber_list.append(subscriber_data)

    return jsonify(subscriber_list)

def create_subscriber(subscriber_data):
    if subscriber_data['event'] == 'subscribed':
        viber_id = subscriber_data['user']['id']
        message_text = get_subscriber_message(viber_id)

        subscriber = Subscriber(
            viber_id=viber_id,
            name=subscriber_data['user']['name'],
            avatar=subscriber_data['user']['avatar'],
            country=subscriber_data['user']['country'],
            language=subscriber_data['user']['language'],
            api_version=subscriber_data['user']['api_version'],
            member_id=message_text
        )


        db.session.add(subscriber)
        db.session.commit()

def delete_subscriber(data):
    if data['event'] == 'unsubscribed':
        viber_id = data['user_id']
        subscriber = Subscriber.query.filter_by(viber_id=viber_id).first()
        if subscriber:
            db.session.delete(subscriber)
            db.session.commit()

def get_subscriber_message(viber_id):
    subscriber_message = SubscriberMessage.query.filter_by(viber_id=viber_id).first()
    if subscriber_message:
        return subscriber_message.message
    return ''

def store_subscriber_message(viber_id, message_text):
    subscriber = Subscriber.query.filter_by(viber_id=viber_id).first()
    subscriber_message = SubscriberMessage.query.filter_by(viber_id=viber_id).first()

    if subscriber:
        db.session.delete(subscriber)
    if subscriber_message:
        db.session.delete(subscriber_message)
    
    db.session.commit()

if __name__ == '__main__':
    app.run()
