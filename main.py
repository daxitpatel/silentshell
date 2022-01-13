import asyncio
import os
from typing import Dict
import uuid
import asyncssh

class EnvManager:
    def __init__(self):
        self.port_str = os.getenv("SSH_SERVER_PORT", "2223")
    
    @property
    def port(self):
        return int(self.port_str)


class User:
    def __init__(self, username: str, channel):
        self.id = str(uuid.uuid4())
        self.username = username
        self.channel = channel

# Data structures for users, chatrooms, and messages (in-memory)
class User:
    def __init__(self, username: str, channel):
        self.id = str(uuid.uuid4())
        self.username = username
        self.channel = channel
        self.room = None
        
class ChatRoom:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.users = set()
        self.messages = []  # Store messages (optional, for message history)

    def add_user(self, user: User):
        self.users.add(user)

    def remove_user(self, user: User):
        self.users.discard(user)

    def broadcast_message(self, message: str, sender: User):
        for user in self.users:
            if user != sender:
                user.channel.write(f"{sender.username}: {message}\r\n")

    def send_message(self, message:str, sender:User):
        self.messages.append({"sender": sender.username, "message": message})

users: Dict[str, User] = {}  #username: User
chat_rooms: Dict[str, ChatRoom] = {}  # room_name: ChatRoom

class SSHServerSession(asyncssh.SSHServerSession):
    def __init__(self, server):
        self.server = server
        self.username = None
        self.user = None

    def connection_made(self, chan):
        self.chan = chan
        self.chan.write('Welcome to the chat server!\r\n')
        
    def data_received(self, data, datatype):
        decoded_data = data.decode().strip()
        if not self.user:
            self.chan.write("Please authenticate first. \r\n")
            return
        
        if decoded_data.startswith("/join"):
            room_name = decoded_data.split(" ")[1]
            self.join_room(room_name)
        elif decoded_data == "/list":
            self.list_rooms()
        elif decoded_data.startswith("/leave"):
            self.leave_room()
        elif decoded_data.startswith("/users"):
            self.list_users()
        else:
            self.send_message(decoded_data)

    def join_room(self, room_name):
        if room_name not in chat_rooms:
            chat_rooms[room_name] = ChatRoom(room_name)
        room = chat_rooms[room_name]
        if self.user.room:
            self.leave_room()
        room.add_user(self.user)
        self.user.room = room
        room.send_message(f"{self.user.username} joined the room.",self.user)
        self.chan.write(f"Joined room {room_name}\r\n")

    def leave_room(self):
        if self.user.room:
            self.user.room.remove_user(self.user)
            self.user.room.send_message(f"{self.user.username} left the room.",self.user)
            self.user.room = None
            self.chan.write(f"Left the room.\r\n")

    def send_message(self, message):
        if not self.user.room:
            self.chan.write(f"You must join a room first.\r\n")
        else:
            self.user.room.broadcast_message(message,self.user)
            self.user.room.send_message(message,self.user)

    def list_rooms(self):
        if len(chat_rooms) == 0:
            self.chan.write("There are no rooms available. \r\n")
            return
        rooms = ", ".join([room.name for room in chat_rooms.values()])
        self.chan.write(f"Available rooms: {rooms}\r\n")

    def list_users(self):
        if self.user.room:
            users_in_room = ", ".join([u.username for u in self.user.room.users])
            self.chan.write(f"Users in {self.user.room.name}: {users_in_room}\r\n")
        else:
            self.chan.write(f"You must join a room first.\r\n")


class SSHServer(asyncssh.SSHServer):
    def session_requested(self):
        return SSHServerSession(self)

    def connection_made(self, conn):
        print('SSH connection received from %s.' %
              conn.get_extra_info('peername')[0])

    def begin_auth(self, username:str):
        # In real application, you would load allowed public keys
        # from database or configuration.
        self.username = username
        self.user = User(username,None)
        return True

    def public_key_auth_supported(self):
        return True

    def validate_public_key(self, public_key, username):
        session_list = self._sessions.copy()
        if session_list:
            #We search the session by username to connect the User to the current session
            for session in session_list:
                if session.username == username:
                    session.user = User(username,session.chan)
                    users[username] = session.user
        # In real application, you would check against
        # the allowed public keys.
        return True
    
async def start_ssh_server(env_manager):
    """Start the ssh server."""
    port = env_manager.port
    print(f"Starting ssh server on {port}")
    await asyncssh.create_server(SSHServer, '127.0.0.1', port)

if __name__ == "__main__":
    env_manager = EnvManager()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_ssh_server(env_manager))
        loop.run_forever()
    except (OSError, asyncssh.misc.ChannelOpenError) as e:
      print("Error:", e)
