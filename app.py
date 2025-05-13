
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from client import P2PClient
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

chat_messages = []
clients = {}

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def handle_login():
    username = request.form.get("username")
    if username:
        session['username'] = username
        if username not in clients:
            clients[username] = P2PClient(
                on_receive_callback=lambda msg: chat_messages.append(msg),
                nickname=username
            )
            clients[username].start()
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/index')
def index():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    return render_template("index.html", username=username)

@app.route('/contacts')
def get_contacts():
    username = session.get('username')
    if not username or username not in clients:
        return jsonify([])
    return jsonify(clients[username].list_contacts())

@app.route('/messages')
def get_messages():
    return jsonify(chat_messages)

@app.route('/send', methods=['POST'])
def send_message():
    username = session.get('username')
    if not username or username not in clients:
        return jsonify({'status': 'error'})
    
    data = request.json
    contact = data['contact']
    message = data['message']
    
    ip, port = contact.split(':')
    clients[username].send_to(ip, int(port), message)
    chat_messages.append(f"<b>Вы → {message}</b>")
    
    return jsonify({'status': 'success'})

@app.route('/export', methods=['POST'])
def export_history():
    username = session.get('username')
    if not username or username not in clients:
        return jsonify({'success': False})
    
    try:
        export_dir = 'exports'
        os.makedirs(export_dir, exist_ok=True)
        filename = clients[username].export_history(export_dir)
        return jsonify({'success': True, 'file': filename})
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({'success': False})

@app.route('/import', methods=['POST'])
def import_history():
    username = session.get('username')
    if not username or username not in clients:
        return jsonify({'success': False})
    
    if 'file' not in request.files:
        return jsonify({'success': False})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False})
    
    try:
        temp_path = f'temp_{username}_history.zip'
        file.save(temp_path)
        success = clients[username].import_history(temp_path)
        os.remove(temp_path)
        return jsonify({'success': success})
    except Exception as e:
        print(f"Import error: {e}")
        return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
