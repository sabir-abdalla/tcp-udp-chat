import socket
import threading

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 55556


def receive(sock):
    # Loop on recvfrom instead of recv
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            if not data:
                break
            print(data.decode("utf-8"), end="")
        except OSError:
            break


def main():
    # SOCK_DGRAM for UDP (no connect() needed)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (SERVER_HOST, SERVER_PORT)

    nickname = input("Choose a nickname: ").strip()
    if not nickname:
        nickname = "Anonymous"
    # First sendto registers this client with the server
    sock.sendto(nickname.encode("utf-8"), server_addr)

    receive_thread = threading.Thread(target=receive, args=(sock,), daemon=True)
    receive_thread.start()

    try:
        while True:
            message = input()
            if message.lower() == "/quit":
                # Send /quit so the server knows to remove us
                sock.sendto("/quit".encode("utf-8"), server_addr)
                break
            sock.sendto(message.encode("utf-8"), server_addr)
    except (KeyboardInterrupt, EOFError):
        sock.sendto("/quit".encode("utf-8"), server_addr)
    finally:
        sock.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()