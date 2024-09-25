from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random


app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)

# Python dictionary. Store connected users. Key is socketid value is username and avatarUrl
users = {}

@app.route('/') 
def index():
    """
    Renders the index template.

    This function is triggered when a user visits the site's root URL. It
    renders the index template, which is a simple HTML page that contains
    a JavaScript script that connects to the Socket.IO server.

    :return: The rendered index template.
    """
    return render_template('index.html')

# We're listening for the connect event
@socketio.on('connect')
def connect():
    """
    Handle the event when a user connects.

    This function is triggered when a user connects to the server. It
    generates a random username and avatar URL, and stores them in the
    users dictionary. It also sends out a 'user_joined' event to all
    connected clients, and a 'set_username' event to the newly connected
    client.

    :param request: The request context.
    """
    username = f'User_{random.randint(1000, 9999)}'
    gender = random.choice(['girl', 'boy'])
    # https://avatar.iran.liara.run/public/boy?username=User_123
    avatar_url = f'https://avatar.iran.liara.run/public/{gender}?username={username}'
    
    users[request.sid] = {'username': username, 'avatarUrl': avatar_url}
    
    emit('user_joined', {'username': username, 'avatarUrl': avatar_url}, broadcast=True)
    
    emit('set_username', {'username': username})
    

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle the event when a user disconnects.

    This function is triggered when the user closes their browser, or
    explicitly disconnects from the server. It removes the user from the
    users dictionary and sends out a 'user_left' event to all connected
    clients.

    :param request: The request context.
    """
    
    user = users.pop(request.sid, None)
    if user:
        emit('user_left', {'username': user['username']}, broadcast=True)
    

@socketio.on('send_message')
def handle_message(data):
    """
    Handle the event when a user sends a message.

    This function is triggered when the user triggers the 'send_message' event.
    It gets the user's username and avatar from the users dictionary and sends
    out a 'new_message' event to all connected clients.

    :param data: A dictionary containing the message sent by the user.
    :type data: dict
    """
    user = users.get(request.sid)
    if user:
        emit('new_message', {'username': user['username'], 'avatar': user['avatar'], 'message': data['message']}, broadcast=True)
        

@socketio.on('update_username')
def handle_update_username(data):
    """
    Handle the event when a user updates their username.

    This function is triggered when the user triggers the 'update_username' event.
    It updates the user's username in the users dictionary and sends out a
    'username_updated' event to all connected clients.

    :param data: A dictionary containing the new username.
    :type data: dict
    """
    old_username = users[request.sid]
    new_username = data['username']
    users[request.sid]['username'] = new_username
    
    emit('username_updated', {'old_username': old_username, 'new_username': new_username}, broadcast=True)   

if __name__=='__main__':
    socketio.run(app, debug=True)