import socket
import sys
import time


HEADER = 64
PORT = 22
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "127.0.0.1"    # socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
info = False

def connect():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect(ADDR)
    return connection


client = connect()


def receive_msg():
    connected = True
    while connected:
        response_length = client.recv(HEADER).decode(FORMAT)
        if response_length:
            response_length = len(response_length)
            msg = client.recv(response_length).decode(FORMAT)
            return f"[{ADDR}]: {msg}"


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    print(f"[SEND]: {msg}")

    client.send(send_length)
    client.send(message)


def login():
    print(receive_msg())
    print(receive_msg())
    username = input("Username: ")
    send(msg=username)

    print(receive_msg())
    password = input("Password: ")
    send(msg=password)

    login_info = receive_msg()
    if login_info != f"[{ADDR}]: [LOGIN SUCCESSFUL]":
        print(login_info)
        login()
    else:
        print(login_info)


login()

while True:
    try:
        send(input("Message:  "))

    except OSError as e:
        if e.__class__ == ConnectionResetError or e.__class__ == ConnectionAbortedError:
            print("[!!CONNECTION TO SERVER HAS BEEN LOST!!]")
            print("[!RECONNECTING IN: !]")
            i = 5
            while i > 0:
                print(i, "...")
                i -= 1
                time.sleep(1)
            try:
                client.close()
                client = connect()
                login()
            except ConnectionRefusedError:
                print("[!!Couldn't establish a connection to the Server!!]")
                sys.exit(0)

        elif e.__class__ == OSError:
            print("[!!SOCKET ERROR!!]")

        else:
            print(f"[!!Error: {e.__class__}!!]")
            break

send(DISCONNECT_MESSAGE)
