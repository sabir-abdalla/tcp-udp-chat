import socket
import threading
import sys

HOST = "127.0.0.1"
PORT = 55555


def receive(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nDisconnected from server.")
                break
            print(data.decode("utf-8"), end="")
        except OSError:
            break
    sock.close()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Could not connect to server. Is it running?")
        sys.exit(1)

    nickname = input("Choose a nickname: ").strip()
    if not nickname:
        nickname = "Anonymous"
    sock.sendall(nickname.encode("utf-8"))

    receive_thread = threading.Thread(target=receive, args=(sock,), daemon=True)
    receive_thread.start()

    try:
        while True:
            message = input()
            if message.lower() == "/quit":
                break
            sock.sendall(f"{message}\n".encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        pass
    finally:
        sock.close()
        print("Disconnected.")


if __name__ == "__main__":
    main()