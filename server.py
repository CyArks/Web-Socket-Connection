import socket
import threading
import hashlib
import time
import mysql.connector
from mysql.connector import errorcode

HEADER = 64
PORT = 22
SERVER = "0.0.0.0"  # socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
OK_RESPONSE = "[Response 200]"
OK_LOGIN_RESPONSE = "[LOGIN SUCCESSFUL]"
FALSE_LOGIN_RESPONSE = "[LOGIN DENIED] Pleas try again!"
LOGIN = "[PLEASE LOG IN]"

config = {
    'user': "root",
    'password': "your sql pw",
    'host': "127.0.0.1",
    'database': "login_data",
    'auth_plugin': 'mysql_native_password'
}

Admin_rights = {
    'command': f'',
}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

user_name = hashlib.sha256(str.encode("root")).hexdigest()
user_password = hashlib.sha256(str.encode("123456789")).hexdigest()


def send(msg, conn):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))

    print(f"[SEND]: {msg}")

    conn.send(send_length)
    conn.send(message)


def receive_msg(conn):
    connected = True
    while connected:
        response_length = conn.recv(HEADER).decode(FORMAT)
        if response_length:
            response_length = len(response_length)
            msg = conn.recv(response_length).decode(FORMAT)
            return msg


def send_response(conn, response):
    message = response.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += (b' ' * (HEADER - len(send_length)))

    print(f"[SENDING RESPONSE]: {response}")

    conn.send(send_length)
    conn.send(message)


def login(conn):
    """Login"""
    time.sleep(1)
    send(conn=conn, msg=LOGIN)
    time.sleep(0.25)
    send(conn=conn, msg="Name: ")
    name = receive_msg(conn=conn)
    print(name)
    send(conn=conn, msg="Password: ")
    password = receive_msg(conn=conn)
    print(password)

    password = hashlib.sha256(str.encode(password)).hexdigest()
    name = hashlib.sha256(str.encode(name)).hexdigest()

    print(f"Trying to login as: {name}")
    if name == user_name and password == user_password:
        send_response(conn=conn, response=OK_LOGIN_RESPONSE)
    else:
        send_response(conn=conn, response=FALSE_LOGIN_RESPONSE)
        login(conn=conn)


def handle_client(conn, addr):
    print(f"[NEW CONNECTION]: {addr} connected.")
    login(conn=conn)

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            print(f"----------------------------------- \n"
                  f"[{addr}]: {msg} \n"
                  f"-----------------------------------")
            if msg == "!create_user":
                send("")
                receive_msg()

            if "!read_login_data_" in str(msg):
                user_id = str(msg).replace("!read_login_data_", "")
                read_login_data(user_ID=user_id)

            if "!read_data" in str(msg):
                pass

            if "!upload_data" in str(msg):
                pass

            if "!" in str(msg):
                pass

            # send_response(conn=conn, response=OK_RESPONSE)
    conn.close()


def upload_data():
    pass


def read_data():
    pass


def read_login_data(user_ID):
    """MySQL read data from specific user"""
    global user_login_data
    try:
        data = mysql.connector.connect(**config)
        cursor = data.cursor()
        cursor.execute("SELECT * FROM login_data")
        row = cursor.fetchone()
        user_login_data = []
        column_names = cursor.column_names
        i = 0
        user_ID = int(user_ID)

        if user_ID > cursor.rowcount:
            print("ID out of Bounds!")

        while row is not None:
            user_login_data.append(row)
            i += 1
            row = cursor.fetchone()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        data.close()
        print("!Error!")

    user_login_data = list(user_login_data[user_ID - 1])
    user_log_data = ""
    for ob in user_login_data:
        user_log_data += (str(ob) + " ")
    user_log_data = user_log_data[:-1]

    print("Searching data... \n" + "Userdata checksum: " +
          hashlib.sha256(str.encode(str(user_log_data))).hexdigest())
    print(f"Userdata id={user_ID}: " + user_log_data)


def start():
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS]: {threading.activeCount() - 1}")
        time.sleep(0.1)


print("[STARTING!]: Server is starting...")
print(f"[INFO!]: Address is: {ADDR}")
start()
