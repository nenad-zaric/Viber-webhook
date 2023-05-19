from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import phone_number_utils

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sqcovnamegkmuj:7b7e16591935aa6b49d3c8735cd9db36aba0904359a4d7fa69c7b17894668406@ec2-3-217-146-37.compute-1.amazonaws.com:5432/dabcmiilq6u3t6'
db = SQLAlchemy(app)

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

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    if data['event'] == 'message':
        viber_id = data['sender']['id']
        message_text = data['message'].get('text', '')
        create_subscriber(data)

        if get_subscriber_message(viber_id) == '':
            store_subscriber_message(viber_id, message_text)

    print(data['event'])

    if data['event'] == 'unsubscribed':
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
            'phone_number': subscriber.phone_number
        }
        subscriber_list.append(subscriber_data)

    return jsonify(subscriber_list)

def create_subscriber(subscriber_data):
    user_data = subscriber_data['sender']
    message_data = subscriber_data['message']
    subscriber = Subscriber.query.filter_by(viber_id=user_data['id']).first()
    #creates new subscriber if it doesnt exist
    if subscriber is None:
        subscriber = Subscriber(
            viber_id=user_data['id'],
            name=user_data['name'],
            avatar=user_data['avatar'],
            country=user_data['country'],
            language=user_data['language'],
            api_version=user_data['api_version'],
            phone_number=get_subscriber_phone_number(message_data)
        )
        print(subscriber)
    else:
        phone_number = get_subscriber_phone_number(message_data)
        if phone_number is not None:
            subscriber.phone_number = phone_number


    db.session.add(subscriber)
    db.session.commit()


def delete_subscriber(data):
    viber_id = data['user_id']
    subscriber = Subscriber.query.filter_by(viber_id=viber_id).first()
    subscriber_message = SubscriberMessage.query.filter_by(viber_id=viber_id).first()

    if subscriber:
        db.session.delete(subscriber)
    if subscriber_message:
        db.session.delete(subscriber_message)

    db.session.commit()

def get_subscriber_message(viber_id):
    subscriber_message = SubscriberMessage.query.filter_by(viber_id=viber_id).first()
    if subscriber_message:
        return subscriber_message.message
    return ''

def get_subscriber_phone_number(data):
    text = data.get('text', '')
    text = phone_number_utils.extract_phone_number(text)

    if(phone_number_utils.is_phone_number(text)):
        return text
    else:
        return None
    

def store_subscriber_message(viber_id, message_text):
    subscriber_message = SubscriberMessage(viber_id=viber_id, message=message_text)
    db.session.add(subscriber_message)
    db.session.commit()

if __name__ == '__main__':
    app.run()
