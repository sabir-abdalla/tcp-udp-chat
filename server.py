import socket
import threading

HOST = "127.0.0.1"
PORT = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()

# Dictionary mapping each client socket to its nickname
clients = {}
# Lock to protect the clients dict from concurrent thread access
clients_lock = threading.Lock()

print(f"Server listening on {HOST}:{PORT}")


def broadcast(message, sender_socket=None):
    with clients_lock:
        disconnected = []
        for client_socket in clients:
            if client_socket is not sender_socket:
                try:
                    client_socket.sendall(message)
                except OSError:
                    disconnected.append(client_socket)
        for client_socket in disconnected:
            del clients[client_socket]


def handle_client(conn, addr):
    try:
        nickname = conn.recv(1024).decode("utf-8").strip()
        if not nickname:
            conn.close()
            return

        with clients_lock:
            clients[conn] = nickname

        print(f"{nickname} connected from {addr}")
        broadcast(f"{nickname} has joined the chat!\n".encode("utf-8"), conn)

        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = f"[{nickname}] {data.decode('utf-8')}"
            print(message.strip())
            broadcast(message.encode("utf-8"), conn)

    except ConnectionResetError:
        pass
    finally:
        with clients_lock:
            nickname = clients.pop(conn, "Unknown")
        print(f"{nickname} disconnected from {addr}")
        broadcast(f"{nickname} has left the chat.\n".encode("utf-8"))
        conn.close()


def main():
    try:
        while True:
            # Block here until a new client connects
            conn, addr = server.accept()
            # Spawn a thread dedicated to this client
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    main()