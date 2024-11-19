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
            rooms[room] = {"members": [], "messages": []}

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
    room = session.get('room')
    if room is None or session.get('name') is None or room not in rooms:
        return redirect(url_for('home'))

    # Get the list of members in the room
    members = [session.get('name')]  # Start with the current user
    for member in rooms[room]['members']:
        if member != session.get('name'):
            members.append(member)

    return render_template('room.html', code=room, messages=rooms[room]['messages'], members=members)

#This function handles incoming messages from clients.
@socketio.on('message')
def message(data):
    room = session.get('room')
    if room not in rooms:
        return
    
    content = {
        "name": session.get('name'),
        "message": data.get('data')
    }
    #Sends the message to the room and appends it to room list
    send(content, to=room)
    rooms[room]['messages'].append(content)
    print(f"{session.get('name')} said: {data.get('data')}")

@socketio.on('connect')
def connect(auth):
    #Gets the room and name from the session
    room = session.get('room')
    name = session.get('name')

    #Room or name not in session and room does not exist
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return

    join_room(room)
    #Sends a message to the room that user has entered
    send({"name": name, "message": "has entered the room"}, to=room)
    
    # Add the user to the room's member list
    rooms[room]['members'].append(name)
    print(f"{name} joined room {room}")

@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    leave_room(room)

    #Removes the user from the room
    if room in rooms:
        rooms[room]['members'].remove(name)
        #If there are no members in the room, delete the room
        if not rooms[room]['members']:
            del rooms[room]

    #Sends a message to the room that user has left
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

if __name__ == '__main__':

    socketio.run(app, debug=True)