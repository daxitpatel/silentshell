# 🌐🔒 SilentShell | SSH Chat: Your Secure Command-Line Chat Hub 💬

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview ✨

SSH Chat is not just another chat app; it's a **command-line communication powerhouse** 💪 that brings real-time conversations right to your terminal! 💻 Leveraging the rock-solid security of SSH, this application allows you to connect, join different chat rooms, and engage in vibrant discussions. 🗣️ This project's heart beats with security, using SSH's encryption to keep your messages private and secure. 🔐

## Key Features 🎉

*   **🔒 Secure Communication:** Every message is encrypted with SSH's robust technology. Your conversations are safe with us!
*   **🚪 Room Management:** Dive into focused discussions by joining diverse chat rooms.
*   **🕹️ User Commands:** Easily interact with the chat server using simple commands.
*   **🔑 SSH-Based:** Utilizes the trusted and familiar SSH protocol for secure communication and authentication.
*   **⚡ Real-Time Chat:** Experience the thrill of instant message delivery within each room.
*   **⌨️ Command Line Interface:**  Interact with other users directly from your terminal.

## Getting Started 🚀

### Prerequisites 📋

Before you jump in, make sure you have the following:

*   **🐍 Python 3.7+:** Our chat server runs on Python.
*   **🔐 OpenSSH Server:** You'll need an OpenSSH server running on your host.
*   **📱 SSH Client:**  Any SSH client will do (like OpenSSH).

### Installation 🛠️

1.  **Clone the Repository** ⬇️
    -   Open your terminal and clone the repository using `git clone`:


```bash
git clone <repository_url>
```

(Replace `<repository_url>` with your repository's URL.)

2.  **Navigate to the Directory** 📂
    -   Change to the cloned directory:


```bash
cd ssh-chat
```

3.  **Install Dependencies** 📦
    -   Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

4. **Generate SSH Keys** 🔑
    - If you dont have ssh key, generate ssh key with this command.

```bash
ssh-keygen
```

- Copy the content of the public key `~/.ssh/id_rsa.pub` to the server's `~/.ssh/authorized_keys` file.

5.  **Run the Server** 🏃‍♂️
    -   Start the SSH Chat server:

```bash
python main.py
```

-   The server starts listening on port `2223`. Ensure this port is open in your server's firewall.

6. **Configure environment variables**:
- Create a `.env` file in the root project directory
- Copy content of sample.env to .env
- Configure the environment variables based on your need.

### Dependencies 📚

Our project uses the following:

*   **asyncssh:** For handling asynchronous SSH connections and server functionalities.
* You can find all necessary dependencies in the `requirements.txt` file.

### Usage 🕹️

1.  **Connect via SSH** 🔗
    -   In your terminal, connect to the server:


```bash
ssh <username>@<server_address> -p 2223
```

-   Replace `<username>` with your server username.
    -   Replace `<server_address>` with the server's IP or domain.
    -   Port `2223` is the default.

2.  **List Available Rooms** 📋
    -   Type `/list` and press Enter to see all available rooms.
3.  **Join a Room** 🚪
    -   Use `/join <room_name>` to enter a room. Example: `/join general`.
4.  **Send Messages** 💬
    -   After joining, just type and press Enter to chat!
5.  **Leave a Room** 🚶
    -   Use `/leave` to exit the current room.
6.  **List Users** 👥
- Type `/users` to list users in current room.

### Environment Variables ⚙️

You can customize the server by setting the following environment variables:

*   **`SSH_SERVER_PORT`**:  The port the SSH server will listen on. (Default: `2223`)
  
  You can configure these in your .env file

## Contributing 🤝

Got ideas or fixes? We'd love to see them! Please submit pull requests or open issues.

## License 📄

This project is licensed under the MIT License. Check out the [LICENSE](LICENSE) file for more details.
