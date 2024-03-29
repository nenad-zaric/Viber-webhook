from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import phone_number_utils
import requests
import json
import vokativi
import os

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(application)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True, server_default=db.text("nextval('subscriber_id_seq'::regclass)"))
    viber_id = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text)
    avatar = db.Column(db.Text)
    country = db.Column(db.Text)
    language = db.Column(db.Text)
    api_version = db.Column(db.Integer)
    phone_number = db.Column(db.Text)


@application.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Event type: "+data['event'])
    if data['event'] == 'message':
        create_subscriber(data)

    if data['event'] == 'conversation_started':
        response = {
            "sender":{
                "name":"Order of the Dragon",
                "avatar":None
            },
            'tracking_data': 'tracking data',
            "type":"text",
            'message': 'Пошаљите свој број телефона како би се пријавили на наш сервис'
        }
        print('Trebalo bi da posalje')
        return json.dumps(response), 200, {'Content-Type': 'application/json'}

    if data['event'] == 'unsubscribed':
        delete_subscriber(data)

    return '', 200

@application.route('/subscribers', methods=['GET'])
def get_subscribers():
    subscribers = Subscriber.query.all()
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
            name=user_data.get('name'),
            avatar=user_data.get('avatar'),
            country=user_data.get('country'),
            language=user_data.get('language'),
            api_version=user_data.get('api_version'),
            phone_number=get_subscriber_phone_number(message_data)
        )
        send_welcome_message(subscriber.viber_id,subscriber.name.split()[0])
    else:
        phone_number = get_subscriber_phone_number(message_data)
        if phone_number is not None:
            subscriber.phone_number = phone_number


    db.session.add(subscriber)
    db.session.commit()


def delete_subscriber(data):
    viber_id = data['user_id']
    subscriber = Subscriber.query.filter_by(viber_id=viber_id).first()

    if subscriber:
        db.session.delete(subscriber)

    db.session.commit()


def get_subscriber_phone_number(data):
    text = data.get('text', '')
    text = phone_number_utils.extract_phone_number(text)

    if phone_number_utils.is_valid_number(text):
        return text
    else:
        return None

def send_welcome_message(viber_id, name):
    name = vokativi.get_value_from_dict(name)
    welcome_message = '''Добродошли у теретану Ред Змаја, '''+name+'''!\n\n''' + '''Са нама можете постићи све своје фитнес циљеве. Наш тим стручњака стоји вам на располагању да вам помогне на сваком кораку.\n\n''' +'''Започните своју фитнес авантуру и осећајте се снажно, здраво и пуно енергије.\n\n''' +'''Желимо вам успех у сваком тренингу и надамо се да ћете уживати у сваком тренутку у теретани Ред Змаја!\n\n'''+'''Срећан тренинг! 🐉💪'''

    authenticationToken = "510a36516c67e493-ab4405fbe63d2564-a30c241fd43964a0"
    api_endpoint = "https://chatapi.viber.com/pa/send_message"
    headers = {"Content-Type": "application/json",
               "X-Viber-Auth-Token": authenticationToken}
    

    image_url = "https://i.postimg.cc/GmdDqvyx/tegovi.png"
    thumbnail_url = "https://i.postimg.cc/wv0LmMvQ/tegovi-thumbnaill.jpg"

    data = {
        "receiver": viber_id,
        "min_api_version":1,
        "sender":{
            "name":"Order of the Dragon",
            "avatar":None
         },
        "tracking_data":"tracking data",
        "type":"picture",
        "media":image_url,
        "text": welcome_message,
        "thumbnail":thumbnail_url
    }

    response = requests.post(api_endpoint, json=data, headers=headers)

    if response.status_code == 200:
        print("Welcome message sent successfully")
    else:
        print("Failed to send welcome message")

def send_message(viber_id, message):
    authenticationToken = "510a36516c67e493-ab4405fbe63d2564-a30c241fd43964a0"
    api_endpoint = "https://chatapi.viber.com/pa/send_message"
    headers = {"Content-Type": "application/json",
               "X-Viber-Auth-Token": authenticationToken}

    data = {
        "receiver": viber_id,
        "min_api_version":1,
        "sender":{
            "name":"Order of the Dragon",
            "avatar":None
         },
        "tracking_data":"tracking data",
        "type":"picture",
        "text": message,
    }

    response = requests.post(api_endpoint, json=data, headers=headers)

    if response.status_code == 200:
        print("Welcome message sent successfully")
    else:
        print("Failed to send welcome message")

if __name__ == '__main__':
    application.run()
