import jwt
from book_table_generator import *
import socket
import sys, os
import threading

DATA_DIRECTORY = 'rooms_availability/'
BUFFER = 4096
DATES = [i.split('.')[0] for i in os.listdir(DATA_DIRECTORY)]
DATA_LOCKS = {i: threading.Lock() for i in DATES}
SECRET = 'EZCOMPANY'

create_data_file(DATA_DIRECTORY)
remove_data_file(DATA_DIRECTORY)



def cert_gen(date, room):
    res = jwt.encode({'date': date, 'room': room}, SECRET, algorithm='HS256')
    return res


def cert_decode(cert):
    res = jwt.decode(cert, SECRET, algorithms="HS256")
    return res


def check_room(date, room, locks):
    filepath = DATA_DIRECTORY + date + '.txt'
    room_exist = False
    room_booked = False
    room_info = None
    R_type = room[0]
    R_num = room[1]
    locks[date].acquire()
    with open(filepath, 'r') as f:
        for line in f:
            l = line.split()
            if l[0] == R_type + str(R_num):
                room_exist = True
                room_info = line
                if l[3] == 'B':
                    room_booked = True
    locks[date].release()
    return room_exist, room_booked, room_info


def book_room(date, room, locks):
    filepath = DATA_DIRECTORY + date + '.txt'
    R_type = room[0]
    R_num = room[1]
    locks[date].acquire()
    filedata = ""
    with open(filepath, 'r') as f:
        for line in f:
            l = line.split()
            if l[0] == R_type + str(R_num):
                line = line.replace('UB', 'B')
            filedata += line
    with open(filepath, 'w') as f:
        f.write(filedata)
    locks[date].release()


def cancel_room(date, room, locks):
    filepath = DATA_DIRECTORY + date + '.txt'
    R_type = room[0]
    R_num = room[1]
    locks[date].acquire()
    filedata = ""
    with open(filepath, 'r') as f:
        for line in f:
            l = line.split()
            if l[0] == R_type + str(R_num):
                line = line.replace('B', 'UB')
            filedata += line
    with open(filepath, 'w') as f:
        f.write(filedata)
    locks[date].release()


def CHK_handler(conn: socket.socket):
    T = conn.recv(BUFFER).decode()
    DATA_LOCKS[T].acquire()
    with open(DATA_DIRECTORY + T + '.txt') as f:
        lines = f.readlines()
        msg = ''.join(lines)
        conn.send(msg.encode())
    DATA_LOCKS[T].release()


def BK_handler(conn: socket.socket):
    T = conn.recv(BUFFER).decode()
    R = conn.recv(BUFFER).decode()
    R_type = R[0].upper()
    R_num = int(R[1])

    room_exist, room_booked, room_info = check_room(T, R, DATA_LOCKS)
    if not room_exist: # if room not exist
        conn.send(b'1')
    elif room_booked: # if room booked
        conn.send(b'2')
    else:
        conn.send(room_info.encode())
        confirmation = conn.recv(BUFFER).decode()
        if confirmation == '1':
            book_room(T, R, DATA_LOCKS)
            cert = cert_gen(T, R_type+str(R_num))
            conn.send(cert.encode())
        else:
            conn.send(b'0')


def EX_handler(conn: socket.socket):
    conn.close()


def MBK_handler(conn: socket.socket):
    cert = conn.recv(BUFFER)
    book_info = cert_decode(cert)
    msg = '\n'.join(['{}: {}'.format(i, j) for i, j in book_info.items()])
    conn.send(msg.encode())




def CAN_handler(conn: socket.socket):
    cert = conn.recv(BUFFER)
    book_info = cert_decode(cert)
    msg = '\n'.join(['{}: {}'.format(i, j) for i, j in book_info.items()])
    conn.send(msg.encode())
    confirmation = conn.recv(BUFFER).decode()
    if confirmation == '1':
        cancel_room(book_info['date'], book_info['room'], DATA_LOCKS)


commandHandler = {}
commandHandler['CHK'] = CHK_handler
commandHandler['BK'] = BK_handler
commandHandler['EX'] = EX_handler
commandHandler['MBK'] = MBK_handler
commandHandler['CAN'] = CAN_handler


def clientHandler(conn: socket.socket):
    while True:
        try:
            command = conn.recv(BUFFER).decode()
        except socket.error:
            exit()
        commandHandler[command](conn)





if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Wrong number of parameters')
        exit()
    HOSTNAME = 'localhost'
    PORT = sys.argv[1]
    PORT = int(PORT)
    HOST = socket.gethostbyname(HOSTNAME)
    try:
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        print('Failed to create socket.')
        sys.exit()
    try:
        serversock.bind((HOST, PORT))
        serversock.listen()
    except socket.error as e:
        print('Failed to bind socket.')
        sys.exit()

    while True:
        print(f"Waiting for connections on port {PORT}")
        conn, addr = serversock.accept()
        t = threading.Thread(target=clientHandler, args=(conn,))
        t.start()

