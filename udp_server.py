import socket

HOST = "127.0.0.1"
PORT = 55556

# Create a DGRAM (datagram) socket instead of STREAM
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

# Track clients by their (ip, port) address tuple
clients = {}

print(f"UDP Server listening on {HOST}:{PORT}")


def broadcast(message, sender_addr=None):
    # Send to every known client address except the sender
    disconnected = []
    for addr in clients:
        if addr != sender_addr:
            try:
                server.sendto(message, addr)
            except OSError:
                disconnected.append(addr)
    for addr in disconnected:
        del clients[addr]

while True:
    try:
        data, addr = server.recvfrom(1024)
        message = data.decode("utf-8").strip()

        # First message from a new address registers the nickname
        if addr not in clients:
            clients[addr] = message
            print(f"{message} joined from {addr}")
            broadcast(f"{message} has joined the chat!\n".encode("utf-8"), addr)
            continue

        # Handle the /quit workaround for disconnect
        if message == "/quit":
            nickname = clients.pop(addr)
            print(f"{nickname} quit from {addr}")
            broadcast(f"{nickname} has left the chat.\n".encode("utf-8"))
            continue

        # Normal message: format and broadcast
        nickname = clients[addr]
        formatted = f"[{nickname}] {message}\n"
        print(formatted.strip())
        broadcast(formatted.encode("utf-8"), addr)

    except KeyboardInterrupt:
        print("\nUDP Server shutting down.")
        break

server.close()