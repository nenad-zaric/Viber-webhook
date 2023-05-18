from flask import Flask, request
import sqlite3

app = Flask(__name__)
DATABASE = 'subscribers.db'

def create_subscriber(subscriber_data):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Check if the event type is 'subscribed'
    if subscriber_data['event'] == 'subscribed':
        viber_id = subscriber_data['user']['id']
        message_text = get_subscriber_message(viber_id)

        # Store the subscriber's data and the content of the first message in the member_id field
        cursor.execute("""
            INSERT INTO subscribers (viber_id, name, avatar, country, language, api_version, member_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            viber_id,
            subscriber_data['user']['name'],
            subscriber_data['user']['avatar'],
            subscriber_data['user']['country'],
            subscriber_data['user']['language'],
            subscriber_data['user']['api_version'],
            message_text
        ))
        conn.commit()

    conn.close()

def get_subscriber_message(viber_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Retrieve the stored message for the subscriber
    cursor.execute("SELECT message FROM subscriber_messages WHERE viber_id = ?", (viber_id,))
    result = cursor.fetchone()

    conn.close()

    if result is not None:
        return result[0]
    else:
        return ''

def store_subscriber_message(viber_id, message_text):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Store the message for the subscriber
    cursor.execute("INSERT INTO subscriber_messages (viber_id, message) VALUES (?, ?)", (viber_id, message_text))
    conn.commit()

    conn.close()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Check if it's a message event and store the message content for the subscriber
    if data['event'] == 'message':
        viber_id = data['sender']['id']
        message_text = data['message'].get('text', '')

        # Store the first message for the subscriber if not already stored
        if get_subscriber_message(viber_id) == '':
            store_subscriber_message(viber_id, message_text)

    # Handle the subscribed event
    if data['event'] == 'subscribed':
        create_subscriber(data)

    return '', 200

if __name__ == '__main__':
    # Create the subscriber_messages table if it doesn't exist
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriber_messages (
            viber_id TEXT PRIMARY KEY,
            message TEXT
        )
    """)
    conn.close()

    app.run()
