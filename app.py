from flask import Flask, render_template, request, redirect, url_for, session, send_file
from client import P2PClient

app = Flask(__name__)
app.secret_key = 'chat-secret-key'

chat_messages = []
client = P2PClient(on_receive_callback=lambda msg: chat_messages.append(msg))
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
    history_path = client.crypto.history_file
    print(f"История сообщений хранится в: {history_path}")
    return render_template("settings.html", history_path=history_path)

@app.route('/export_history')
def export_history():
    history_path = client.crypto.history_file
    return send_file(history_path, as_attachment=True, download_name='chat_history.enc')

@app.route('/import_history', methods=['POST'])
def import_history():
    if 'history_file' not in request.files:
        return 'Файл не выбран', 400
    file = request.files['history_file']
    if file.filename == '':
        return 'Файл не выбран', 400
    if file:
        file.save(client.crypto.history_file)
        client.chat_history = client.crypto.load_chat_history()
        return redirect(url_for('settings'))

@app.route('/chat/<chat_id>')
def chat(chat_id):
    if chat_id not in session.get('opened_chats', []):
        session.setdefault('opened_chats', []).append(chat_id)
    return render_template("chat.html", chat_id=chat_id, messages=chat_messages)


@app.route('/send/<chat_id>', methods=["POST"])
def send(chat_id):
    msg = request.form.get("message")
    if msg:
        client.send_to_all(msg)
        chat_messages.append(f"Вы ({chat_id}): {msg}")
    return redirect(url_for('chat', chat_id=chat_id))


if __name__ == '__main__':
    app.run(debug=True)
