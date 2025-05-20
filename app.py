
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from client import P2PClient
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

clients = {}  # {session_id: client}
messages = {}  # {session_id: [messages]}
message_counter = 0

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/login', methods=["POST"])
def handle_login():
    nickname = request.form.get("nickname")
    server_choice = request.form.get("serverChoice")
    
    if nickname:
        if server_choice == "local":
            server_host, server_port = "127.0.0.1", 3000
        elif server_choice == "smart":
            server_host, server_port = "smartcontrol.su", 3000
        else:
            custom_addr = request.form.get("customServer", "").split(":")
            if len(custom_addr) != 2:
                return "Неверный формат адреса сервера", 400
            server_host, server_port = custom_addr[0], int(custom_addr[1])

        session['nickname'] = nickname
        if 'id' not in session:
            session['id'] = os.urandom(16).hex()
        
        session_id = session['id']
        if session_id not in clients:
            clients[session_id] = P2PClient(
                on_receive_callback=lambda msg: handle_message(session_id, msg),
                nickname=nickname,
                server_host=server_host,
                server_port=server_port
            )
            messages[session_id] = []
            clients[session_id].start()
        
        return redirect(url_for('chat'))
    return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'nickname' not in session:
        return redirect(url_for('login'))
    return render_template('chat.html')

def handle_message(session_id, msg):
    global message_counter
    message_counter += 1
    messages[session_id].append({
        'id': message_counter,
        'text': msg
    })

@app.route('/contacts')
def get_contacts():
    if 'id' not in session:
        return jsonify([])
    
    client = clients.get(session['id'])
    if not client:
        return jsonify([])
        
    contacts = []
    for addr in client.list_contacts():
        ip, port = addr.split(':')
        nickname = client.get_nickname((ip, int(port)))
        contacts.append({
            'addr': addr,
            'nickname': nickname
        })
    return jsonify(contacts)

@app.route('/messages')
def get_messages():
    if 'id' not in session:
        return jsonify([])
    return jsonify(messages.get(session['id'], []))

@app.route('/send', methods=['POST'])
def send_message():
    if 'id' not in session:
        return jsonify({'success': False})
    
    client = clients.get(session['id'])
    if not client:
        return jsonify({'success': False})
    
    data = request.json
    contact = data['contact']
    message = data['message']
    
    ip, port = contact.split(':')
    client.send_to(ip, int(port), message)
    handle_message(session['id'], f"<b>Вы → {message}</b>")
    
    return jsonify({'success': True})

@app.route('/export', methods=['POST'])
def export_history():
    if 'id' not in session:
        return jsonify({'success': False})
    
    client = clients.get(session['id'])
    if not client:
        return jsonify({'success': False})
    
    try:
        export_dir = 'exports'
        os.makedirs(export_dir, exist_ok=True)
        filename = client.export_history(export_dir)
        return send_file(filename, as_attachment=True)
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({'success': False})

@app.route('/import', methods=['POST'])
def import_history():
    if 'id' not in session or 'file' not in request.files:
        return jsonify({'success': False})
    
    client = clients.get(session['id'])
    if not client:
        return jsonify({'success': False})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False})
    
    try:
        temp_path = f'temp_{session["id"]}_history.zip'
        file.save(temp_path)
        success = client.import_history(temp_path)
        if success:
            for msg in client.history.messages:
                handle_message(session['id'], f"{msg['sender']} → {msg['text']}")
        os.remove(temp_path)
        return jsonify({'success': success})
    except Exception as e:
        print(f"Import error: {e}")
        return jsonify({'success': False})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
