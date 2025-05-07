import click
import socket
import requests
import threading

# Constants
MAIN_SERVER_URL = "http://localhost:5000"  # Update this with your deployed server URL

@click.group()
def cli():
    "Chat CLI Tool"
    pass

@cli.command()
def start_server():
    "Start a chat server."
    port = click.prompt("Enter the port to host the server on", type=int)
    public = click.confirm("Do you want to create a public server?", default=False)

    # Register with the main server
    response = requests.post(f"{MAIN_SERVER_URL}/register", json={"port": port, "public": public})

    if response.status_code == 201:
        data = response.json()
        if public:
            click.echo(f"Public server registered at port {port}.")
        else:
            click.echo(f"Private server registered. Your key: {data['key']}")
        
        # Start listening for clients
        start_chat_server(port, public)
    else:
        click.echo(f"Failed to register server: {response.json().get('error')}")

def start_chat_server(port, public):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    click.echo(f"Chat server started on port {port}. Waiting for connections...")

    def handle_client(client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if not message:
                    break
                click.echo(f"Client: {message}")
                for client in clients:
                    client.sendall(message.encode("utf-8"))
            except:
                break
        client_socket.close()

    clients = []

    try:
        while True:
            client_socket, addr = server_socket.accept()
            click.echo(f"Client connected from {addr}")
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket,)).start()
    except KeyboardInterrupt:
        click.echo("Shutting down server...")
        server_socket.close()
        if public:
            # Update main server to remove public server
            requests.post(f"{MAIN_SERVER_URL}/remove", json={"port": port})
        exit()

@cli.command()
def join():
    "Join a chat server."
    name = click.prompt("Enter your name")
    public = click.confirm("Do you want to join a public server?", default=False)

    if public:
        response = requests.get(f"{MAIN_SERVER_URL}/public_servers")
        if response.status_code == 200:
            public_servers = response.json()
            if not public_servers:
                click.echo("No public servers available.")
                return

            click.echo("Available public servers:")
            for i, server in enumerate(public_servers):
                click.echo(f"[{i}] {server['ip']}:{server['port']}")

            choice = click.prompt("Select a server to join", type=int)
            if choice < 0 or choice >= len(public_servers):
                click.echo("Invalid choice.")
                return

            server = public_servers[choice]
            connect_to_server(server['ip'], server['port'], name)
        else:
            click.echo("Failed to fetch public servers.")
    else:
        key = click.prompt("Enter the private server key")
        response = requests.get(f"{MAIN_SERVER_URL}/lookup", params={"key": key})
        if response.status_code == 200:
            server = response.json()
            connect_to_server(server['ip'], server['port'], name)
        else:
            click.echo("Server not found.")

def connect_to_server(ip, port, name):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, int(port)))
        click.echo(f"Connected to server at {ip}:{port}")

        def receive_messages():
            while True:
                try:
                    message = client_socket.recv(1024).decode("utf-8")
                    if not message:
                        break
                    click.echo(f"{message}")
                except:
                    break

        threading.Thread(target=receive_messages, daemon=True).start()

        while True:
            message = input("> ")
            if message.lower() == "exit":
                client_socket.close()
                break
            client_socket.sendall(f"{name}: {message}".encode("utf-8"))
    except Exception as e:
        click.echo(f"Failed to connect to server: {e}")

if __name__ == "__main__":
    cli()