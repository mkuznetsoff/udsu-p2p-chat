from flask import Flask, render_template, request, redirect, url_for, session
from client import P2PClient

app = Flask(__name__)
app.secret_key = 'chat-secret-key'

chat_messages = []
client = P2PClient(on_receive_callback=lambda msg: chat_messages.append(msg), nickname="Server")
client.start()

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def handle_login():
    username = request.form.get("username")
    if username:
        session['username'] = username
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/index')
def index():
    username = session.get('username', None)
    if not username:
        return redirect(url_for('login'))
    return render_template("index.html", username=username)

@app.route('/settings')
def settings():
    return render_template("settings.html")

@app.route('/contacts')
def get_contacts():
    contacts = client.list_contacts()
    return jsonify(contacts)

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    contact = data['contact']
    message = data['message']
    ip, port = contact.split(':')
    client.send_to(ip, int(port), message)
    return jsonify({'status': 'success'})


@app.route('/send/<chat_id>', methods=["POST"])
def send(chat_id):
    msg = request.form.get("message")
    if msg:
        client.send_to_all(msg)
        chat_messages.append(f"Вы ({chat_id}): {msg}")
    return redirect(url_for('chat', chat_id=chat_id))


if __name__ == '__main__':
    app.run(debug=True)
