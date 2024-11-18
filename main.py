from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'passwordpleasedontsteal!'
socketio = SocketIO(app)

rooms = {}

#Creates a unique code for a room
def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(string.ascii_uppercase)

        if code not in rooms:
            break

    return code


@app.route('/', methods=['GET', 'POST'])
def home():
    session.clear()
    if request.method == 'POST':
        #Gets the information from the form
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        #Name or code not entered
        if not name:
            return render_template('home.html', error="Please enter a name.", code=code, name=name)
        if join != False and not code:
            return render_template('home.html', error="Please enter a room code.", code=code, name=name)
        
        #Creates a room if the create button is pressed
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}

        #Room does not exist
        elif code not in rooms:
            return render_template('home.html', error="Room does not exist.", code=code, name=name)
        
        #Adds the room and name to the session
        session['room'] = room
        session['name'] = name
 
        return redirect(url_for('room'))
    
    return render_template('home.html')

@app.route('/room')
def room():
    return render_template('room.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)