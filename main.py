import asyncio
import os
from typing import Dict, Optional, Set
import uuid
import asyncssh

class UserManager:
    """
    Manages user-related data and operations.

    This class handles user data, such as user names and their associated channels.
    """
    def __init__(self):
        """Initializes the UserManager."""
        self.users: Dict[str, User] = {}  # username: User

    def get_user_data(self, user_name: str) -> Dict[str, str]:
        """
        Retrieves user data.
        Args:
            user_name (str): The username of the user.

        Returns:
            Dict[str, str]: A dictionary containing the user's data.
        """
        user_data: Optional[Dict[str, str]] = {
                "name": user_name,
                "HOME": f"/home/{user_name}",
            }
        return user_data
    
    def add_user(self, user):
        """Adds a user to the list of users"""
        self.users[user.username] = user
    
    def get_user(self, username):
        """Get a user by its name"""
        return self.users.get(username)
    
class RoomManager:
    """
    Manages chat rooms and their operations.

    This class handles the creation, joining, and leaving of chat rooms, as well as message broadcasting.
    """
    def __init__(self):
        """Initializes the RoomManager."""
        self.chat_rooms: Dict[str, ChatRoom] = {}  # room_name: ChatRoom

    def get_room(self, room_name: str) -> "ChatRoom":
        """
        Retrieves a chat room by name, creating it if it doesn't exist.
        
        Args:
            room_name (str): The name of the chat room.

        Returns:
            ChatRoom: The requested chat room.
        """
        if room_name not in self.chat_rooms:
            self.chat_rooms[room_name] = ChatRoom(room_name)
        return self.chat_rooms[room_name]
    
    def get_rooms(self) -> list:
        """Returns the list of available rooms"""
        return self.chat_rooms.values()


class User:
    """
    Represents a user in the chat application.

    Attributes:
        id (str): A unique identifier for the user.
        username (str): The username of the user.
        channel: The SSH channel associated with the user.
        room (Optional[ChatRoom]): The chat room the user is currently in.
    """
    def __init__(self, username: str, channel=None):
        """
        Initializes a new User.

        Args:
            username (str): The username of the user.
            channel: The SSH channel for communication with the user.
        """
        self.id = str(uuid.uuid4())
        self.username = username
        self.channel = channel
        self.room = None

class ChatRoom:
    """
    Represents a chat room where users can interact.

    Attributes:
        id (str): A unique identifier for the chat room.
        name (str): The name of the chat room.
        users (Set[User]): The set of users currently in the chat room.
        messages (list): A list of messages sent in the chat room.
    """
    def __init__(self, name: str):
        """
        Initializes a new ChatRoom.

        Args:
            name (str): The name of the chat room.
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.users: Set[User] = set()
        self.messages = []  # Store messages (optional, for message history)

    def add_user(self, user: User):
        """Adds a user to the chat room."""
        self.users.add(user)

    def remove_user(self, user: User):
        """Removes a user from the chat room."""
        self.users.discard(user)

    def broadcast_message(self, message: str, sender: User):
        """Broadcasts a message to all users in the chat room except the sender."""
        for user in self.users:
            if user != sender:
                user.channel.write(f"{sender.username}: {message}\r\n")

    def send_message(self, message:str, sender:User):
        """Sends a message and store it in the list of messages"""
        self.messages.append({"sender": sender.username, "message": message})

class CommandHandler:
    """
    Parses and processes user commands in the chat application.

    This class contains methods to handle different types of user commands like joining, leaving, listing rooms, etc.
    """
    def __init__(self, user_manager:UserManager, room_manager:RoomManager, session):
        """Initializes the CommandHandler."""
        self.user_manager = user_manager
        self.room_manager = room_manager
        self.session = session
        
    def handle_command(self, decoded_data: str):
        """Handles the command sent by the user."""
        if decoded_data.startswith("/join"):
            parts = decoded_data.split(" ")
            if len(parts) < 2:
                self.session.chan.write("Usage: /join <room_name>\r\n")
                return
            room_name = parts[1]
            self.join_room(room_name)
        elif decoded_data == "/list":
            self.list_rooms()
        elif decoded_data.startswith("/leave"):
            self.leave_room()
        elif decoded_data.startswith("/users"):
            self.list_users()
        else:
            self.send_message(decoded_data)

    def join_room(self, room_name: str):
        """Handles the /join command."""
        room = self.room_manager.get_room(room_name)
        if self.session.user.room:
            self.leave_room() #If already in a room, leave it
        room.add_user(self.session.user)
        self.session.user.room = room
        room.send_message(f"{self.session.user.username} joined the room.",self.session.user)
        self.session.chan.write(f"Joined room {room_name}\r\n")
    
    def leave_room(self):
        """Handles the /leave command."""
        if self.session.user.room:
            self.session.user.room.remove_user(self.session.user)
            self.session.user.room.send_message(f"{self.session.user.username} left the room.",self.session.user)
            self.session.user.room = None
            self.session.chan.write(f"Left the room.\r\n")

    def send_message(self, message):
        """Sends a message in the current room."""
        if not self.session.user.room:
            self.session.chan.write(f"You must join a room first.\r\n")
        else:
            self.session.user.room.broadcast_message(message,self.session.user)
            self.session.user.room.send_message(message,self.session.user)

    def list_rooms(self):
        """Handles the /list command."""
        if len(self.room_manager.get_rooms()) == 0:
            self.session.chan.write("There are no rooms available. \r\n")
            return
        rooms = ", ".join([room.name for room in self.room_manager.get_rooms()])
        self.session.chan.write(f"Available rooms: {rooms}\r\n")

    def list_users(self):
        """Handles the /users command."""
        if self.session.user.room:
            users_in_room = ", ".join([u.username for u in self.session.user.room.users])
            self.session.chan.write(f"Users in {self.session.user.room.name}: {users_in_room}\r\n")
        else:
            self.session.chan.write(f"You must join a room first.\r\n")
            
class SSHServerSession(asyncssh.SSHServerSession):
    """
    Represents an SSH session for a connected user.

    This class handles the communication with a connected SSH client, including authentication and command processing.
    """
    def __init__(self, server, user_manager:UserManager, room_manager:RoomManager):
        """
        Initializes a new SSHServerSession.
        """
        self.server = server #type: ignore
        self.username = None
        self.user = None
        self.user_manager = user_manager
        self.room_manager = room_manager
        self.command_handler = CommandHandler(user_manager,room_manager, self)
    
    def connection_made(self, chan):
        """Called when a new connection is made."""
        self.chan = chan
        self.chan.write('Welcome to the chat server!\r\n')
    
    def data_received(self, data, datatype):
        """Called when data is received from the client."""
        decoded_data = data.decode().strip()
        if not self.user:
            self.chan.write("Please authenticate first. \r\n")
            return
        self.command_handler.handle_command(decoded_data)
        
class SSHServer(asyncssh.SSHServer):
    """
    Represents an SSH server that handles incoming connections.

    This class is responsible for accepting new SSH connections, managing user authentication,
    and creating sessions for connected users.
    """
    def connection_made(self, conn):
        """Called when a new connection is made."""
        print('SSH connection received from %s.' %
              conn.get_extra_info('peername')[0])

    def begin_auth(self, username:str):
        """Called when a user attempts to authenticate."""
        self.username = username
        return True

    def public_key_auth_supported(self) -> bool:
        """Indicates that public key authentication is supported."""
        return True
    
    def validate_public_key(self, public_key, username) -> bool:
        """Validates a user's public key."""
        session_list = self._sessions.copy()
        user = self.user_manager.get_user(username)
        if session_list:
            #We search the session by username to connect the User to the current session
            for session in session_list:
                if session.username == username:
                    if not user:
                        session.user = User(username,session.chan)
                        self.user_manager.add_user(session.user)
                    else:
                        session.user = user
                        session.user.channel = session.chan
        return True
    
    def session_requested(self):
        """
        Called when a new session is requested.

        Returns:
            SSHServerSession: A new session for the connected user.
        """
        return SSHServerSession(self,self.user_manager,self.room_manager)
    
    def __init__(self, user_manager:UserManager, room_manager:RoomManager) -> None:
        self.user_manager = user_manager
        self.room_manager = room_manager

async def start_ssh_server(user_manager:UserManager, room_manager:RoomManager):
    """
    Starts the SSH server.

    This function creates an SSH server that listens on the specified port and uses the
    SSHServer class to handle incoming connections.
    """
    port = int(os.getenv("SSH_SERVER_PORT", "2223"))
    print(f"Starting ssh server on {port}")
    await asyncssh.create_server(lambda: SSHServer(user_manager, room_manager), '127.0.0.1', port)
    
if __name__ == "__main__":
    user_manager = UserManager()
    room_manager = RoomManager()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_ssh_server(user_manager, room_manager))
        loop.run_forever()
    except (OSError, asyncssh.misc.ChannelOpenError) as e:
      print("Error:", e)

