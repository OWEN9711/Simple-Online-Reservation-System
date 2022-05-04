# Online Reservation System

This project is done for the mini project for the course IS496, the NetId of the team member are:

shaojun3, boyu4, xiuyuan7

## 1. Instructions on how to use the program

Go to the project folder

### start the server

the hostname is indicated by a global variable in *server.py*, the default value is:
```python
hostname = 'localhost'
```

when we run the server, we only need to provide 1 additional parameter, which is its portnumber:

```bash
python server.py [portnnumber]
```

### run the client

the hostname should be the one on which the server is running

```bash
python client.py [hostname] [portnumber]
```

### Checking Available Rooms

there should be a *file* storing rooms availability, when reading it, we need to apply lock

**command**: CHK

### Booking Hotel Rooms

change the *server file*, return a **certificate for booking** (using JWT)

**command**: BK



### Check My Booking

send the booking certificate to server to get the information, display the information

**command**: MBK

### Cancel My Booking

send the certificate for booking and then change the *server file*

**command**: CAN

### Exit

to exit the program

**Command**: EX


## 2. Special Notices

### (1) the data file for room availability 
The rooms information all store in the folder indicated by a global variable in *server.py*, the default value is: 
```python
DATA_DIRECTORY = 'rooms_availability/'
```

### (2) about *book_table_generator.py*
Our reservation system only accept reservation for date from today to 10 days in the future, the reservation data file for yesterday will be erased and the data file for the 10th day in the future will be created automatically the first time we run the server today, these are done in the file *book_table_generator.py*

### (3) protection of the data file
The server of this program is multi-threaded, which means that it can serve multiple clients at the same time, as a result, each time we read and write the data files for rooms availability, we need to acquire a lock to prevent potential read write error

### (4) the data file for order
The data of the order that our customers placed reside in the file specify by a global variable in client.py, the default value is: 
```python
MY_BOOKING_FILEPATH = 'my_booking.txt'
```

### (5) about order encryption
The order that our customers placed is encrypted by JSON Web Token(JWT), the secret key is specified by a global variable in *server.py*, the default value is:
```python
SECRET = "EZCOMPANY"
```
the payload that we provide is the *date* and *room number*, and the algorithm used for encryption is *HS256*. Here's an example of our encryption process:
```python
jwt.encode({
    'date':'2022-05-07',
    'room':'A1'
}, "EZCOMPANY", algorithm='HS256')
```

## 3. Design

(1) our code utilize TCP protocol to transfer command and data between server and client.

(2) our server is multi-threaded so that it can serve different clients at the same time. And we have apply lock appropriately to prevent booking conflicts.

(3) our program provide some encryption schemes using JWT to prevent users from changing the order information.

(4) our code is robust because we perform input check for our program so our program is unlikely to crash due to unexpected user input.

## 4. Contributions

The code is written by Shaojun Zheng(shaojun3).

The other 2 team members Boyu Zhang(boyu4) and Xiuyuan Wang(xiuyuan7) are responsible for writing report and recording demo video.


