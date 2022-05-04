import socket
import sys
import datetime
import re

BUFFER = 4096
MY_BOOKING_FILEPATH = 'my_booking.txt'


def book_list(filepath):
    f = open(filepath, 'r')
    lines = f.readlines()
    if len(lines) == 0:
        print('You do not have any booking')
    else:
        print('Your booking are listed as follow: ')
    for i in range(len(lines)):
        print(str(i+1)+' '+lines[i])
    f.close()
    return lines

def get_date():
    """
    this function is for getting date from user
    :return: a date string of date in yyyy-mm-dd format.
    """
    while True:
        T = input('Please enter the date you want to book in a yyyy-mm-dd format: ').strip()
        while re.search('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', T) is None:
            T = input('The date you provide should follow the yyyy-mm-dd format, please re-enter: ').strip()
        year, month, day = T.split('-')
        year, month, day = int(year), int(month), int(day)
        if datetime.datetime.now() + datetime.timedelta(days=10) < datetime.datetime(year, month, day):
            print('We only accept reservations 10 days in advance, please input a date prior to {}'.format(
                datetime.datetime.now().date() + datetime.timedelta(days=11)))
        elif datetime.datetime(year, month, day).date() < datetime.datetime.now().date():
            print('Please input a date from today')
        else:
            break
    return T


def CHK_handler(conn: socket.socket):
    conn.send(b'CHK')
    T = get_date()
    conn.send(T.encode())
    info = conn.recv(BUFFER).decode()
    print(info)


def BK_handler(conn: socket.socket):
    conn.send(b'BK')
    T = get_date()
    conn.send(T.encode())

    R = input('Please enter the room number you want to book in a Tn format(T is the type of the room and n is its number): ').strip()
    while len(R) > 2 or not R[0].isalpha() or not R[1].isdigit():
        R = input('Wrong format of room number, please re-enter: ').strip()

    conn.send(R.encode())
    res = conn.recv(BUFFER).decode()
    if res == '2':
        print('the room is already booked by other customer')
    elif res == '1':
        print('the room number does not exist')
    else:
        room_info = res
        info = room_info.split()
        confirmation = input('the room you want to book is {}, it is a {}, the price is {}, please confirm(y for yes and n for no): '.format(info[0], info[1], info[2])).strip().upper()

        while confirmation not in ['Y', 'YES', 'N', 'NO']:
            confirmation = input('the room you want to book is {}, it is a {}, the price is {}, please confirm(y for yes and n for no): '.format(info[0], info[1],
                                                                                          info[2])).strip().upper()

        if confirmation in ['Y', 'YES']:
            conn.send(b'1')
            cert = conn.recv(BUFFER)
            with open(MY_BOOKING_FILEPATH, 'a+') as f:
                f.write(cert.decode()+'\n')
            print('You have successfully booked the room')
        else:
            conn.send(b'0')
            conn.recv(BUFFER)
            print('Canceled')


def EX_handler(conn:socket.socket):
    conn.send(b'EX')
    conn.close()


def MBK_handler(conn: socket.socket):
    conn.send(b'MBK')
    lines = book_list(MY_BOOKING_FILEPATH)
    while True:
        book_num = input('Please enter the booking you want to check: ').strip()
        if book_num.isdigit() and int(book_num) <= len(lines):
            break
        print('Invalid booking number')
    book_num = int(book_num)
    cert = lines[book_num-1][:-1]
    conn.send(cert.encode())
    book_info = conn.recv(BUFFER).decode()
    print(book_info)


def CAN_handler(conn: socket.socket):
    conn.send(b'CAN')
    lines = book_list(MY_BOOKING_FILEPATH)
    while True:
        book_num = input('Please enter the booking you want to cancel: ').strip()
        if book_num.isdigit() and int(book_num) <= len(lines):
            break
        print('Invalid booking number')
    book_num = int(book_num)
    conn.send(lines[book_num-1][:-1].encode())
    lines.pop(book_num-1)
    with open(MY_BOOKING_FILEPATH, 'w') as f:
        f.writelines(lines)
    book_info = conn.recv(BUFFER).decode()
    print('This is the booking you want to cancel: ')
    print(book_info)
    confirmation = input('are you sure you want to cancel?(Y for yes and N for no)').strip().upper()
    while confirmation not in ['Y', 'YES', 'N', 'NO']:
        confirmation = input('Please enter Y for yes and N for no: ').strip().upper()
    if confirmation in ['Y', 'YES']:
        conn.send(b'1')
        print('booking cancel successfully')
    else:
        conn.send(b'0')



commandHandler = {}
commandHandler['CHK'] = CHK_handler
commandHandler['BK'] = BK_handler
commandHandler['EX'] = EX_handler
commandHandler['MBK'] = MBK_handler
commandHandler['CAN'] = CAN_handler


if __name__ == '__main__':
    # TODO: Validate input arguments
    if len(sys.argv) != 3:
        print('Wrong number of parameters')
        exit()
    HOSTNAME, PORT = sys.argv[1:]
    PORT = int(PORT)
    HOST = socket.gethostbyname(HOSTNAME)
    # TODO: create a socket with UDP or TCP, and connect to the server
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
    except socket.error as msg:
        # print(f'Failed to create socket. Error Code : {str(msg[0])}\n Message: {msg[1]}')
        sys.exit()
    print('Welcome to our hotel reservation services!')
    while True:
        print('Please use the following commands:')
        print('CHK-checking rooms availability, '
              'BK-booking rooms, MBK-check your booking, CAN-cancel booking, EX-quit')
        command = input('>').strip().upper()
        while command not in commandHandler:
            print('command not found.')
            command = input('>').strip().upper()
        commandHandler[command](s)
        if command == 'EX':
            break