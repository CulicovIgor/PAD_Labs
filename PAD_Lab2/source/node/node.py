import socket
import struct
import threading
import random
from source.data.data_creator import Object

names = ['Igor', 'Xenia', 'Ivan', 'Pavel', 'Iana', 'Aliona']


class Node(threading.Thread):

    def __init__(self, thread_id, name, port):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.list_of_objects = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', port))
        self.create_startup_data(random.randint(0, 5))

    def create_startup_data(self, number):
        for x in range(0, number + 1):
            data = Object()
            data.name = random.choice(names)
            data.age = random.randrange(30)
            self.list_of_objects.append(data.to_json())

    def run(self):
        print("Starting " + self.name)
        #print("List ".join(self.list_of_objects))
        multicast_group = '224.3.29.71'
        server_address = ('', 10000)

        # Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind to the server address
        sock.bind(server_address)
        group = socket.inet_aton(multicast_group)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        while True:
            print('\nwaiting to receive message')
            data, address = sock.recvfrom(1024)

            print('received %s bytes from %s' % (len(data.decode()), address))
            print(data.decode())

            print('sending acknowledgement to', address)
            self.socket.sendto('ack'.encode(), address)
