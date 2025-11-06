from flask import Flask, render_template, request, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
import uuid
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret!')
socketio = SocketIO(app, cors_allowed_origins="*")  # uses eventlet or gevent when running with gunicorn

@app.route('/')
def index():
    # If ?room=xxx provided, show it prefilled (auto-join flow)
    room = request.args.get('room', '')
    return render_template('index.html', room=room)

# Create short room id and join
@socketio.on('create-room')
def on_create_room():
    room_id = str(uuid.uuid4())[:8]
    join_room(room_id)
    emit('room-created', {'room': room_id})

# Join a room
@socketio.on('join-room')
def on_join(data):
    room_id = data.get('room')
    join_room(room_id)
    emit('peer-joined', {'id': request.sid}, room=room_id, include_self=False)

# Generic signaling forwarding within room (offer/answer/candidate)
@socketio.on('signal')
def on_signal(data):
    room = data.get('room')
    # forward to other peers in room
    emit('signal', data, room=room, include_self=False)

@socketio.on('disconnecting')
def on_disconnecting():
    # notify peers (rooms includes socket id as well)
    for r in list(socketio.server.rooms(request.sid)):
        if r != request.sid:
            emit('peer-left', {'id': request.sid}, room=r, include_self=False)

if __name__ == '__main__':
    # local dev
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
