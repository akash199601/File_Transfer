from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create-room')
def create_room():
    room_id = str(uuid.uuid4())[:8]
    join_room(room_id)
    emit('room-created', {'room_id': room_id})

@socketio.on('join-room')
def on_join(data):
    room_id = data['room']
    join_room(room_id)
    emit('peer-joined', room=room_id, include_self=False)

@socketio.on('signal')
def on_signal(data):
    room_id = data['room']
    emit('signal', data, room=room_id, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8765)
