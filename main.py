from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'passwordpleasedontsteal!'
socketio = SocketIO(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    socketio.run(app, debug=True)