import socket
import struct
import threading
import random
import json
from source.data.data_creator import Object

names = ['Igor', 'Xenia', 'Ivan', 'Pavel', 'Iana', 'Aliona']

diction = {
    "<": lambda a, b: not a < b,
    ">": lambda a, b: not a > b,
    "<=": lambda a, b: not a >= b,
    ">=": lambda a, b: not a >= b,
    "=": lambda a, b: not a == b,
    "!=": lambda a, b: a == b
}

class Node(threading.Thread):
    def __init__(self, name, port, connected_ports):
        threading.Thread.__init__(self)
        self.name = name
        self.list_of_objects = []
        self.connected_ports = connected_ports
        self.port = port
        self.last_request = ''
        self.create_startup_data(random.randint(0, 5))
        self.ip_address = '127.0.0.1'

    def filtering(self, list_it, expr):
        if expr == "":
            return list_it
        tmp_list = list_it
        print(tmp_list)
        expr_data = expr.split()
        remove_list = []
        symbol = expr_data[1]
        comp = expr_data[2]
        try:
            comp = int(expr_data[2])
        except ValueError:
            pass
        for it in list_it:
            if type(comp) == int:
                print("Is int")
                field_name = it[expr_data[0]]
            else:
                field_name = str(it[expr_data[0]])
            if diction[symbol](field_name, comp):
                remove_list.append(it)
        for it in remove_list:
            list_it.remove(it)

    def create_startup_data(self, number):
        for x in range(0, number + 1):
            data = Object()
            data.name = random.choice(names)
            data.age = random.randrange(30)
            self.list_of_objects.append(data)

    def get_conn_socket_data(self, ip, port, msg, return_list):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        print(json.dumps(msg))
        s.send(json.dumps(msg).encode())
        data = s.recv(1024)
        if data.decode() == '':
            s.close()
        else:
            data = json.loads(data.decode())
            for obj in data:
                return_list.append(obj)
            s.close()

    def handle_tcp(self):
        print("Starting tcp" + self.name)
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.bind((self.ip_address, self.port))
        sock_tcp.listen()
        while True:
            print('\nwaiting to receive message')
            conn, address = sock_tcp.accept()
            hm = threading.Thread(name='handle_tcp_request', target=self.handle_tcp_request, args=(conn, address))
            hm.start()

    def handle_tcp_request(self, conn, address):
        data = conn.recv(1024)
        print('received %s bytes from %s' % (len(data.decode()), address))
        print(data.decode())
        # check data received
        request = json.loads(data.decode())
        if self.last_request == request["uuid"]:
            conn.send(''.encode())
        else:
            self.last_request = request["uuid"]
            # connected nodes data collecting
            return_list = []
            if request["depth"] > 0:
                # multithreaded conn method
                list1 = []
                request["depth"] -= 1
                for port in self.connected_ports:
                    thread = threading.Thread(name='get_conn_socket_data', target=self.get_conn_socket_data,
                                              args=('127.0.0.1', port, request, return_list))
                    thread.start()
                    list1.append(thread)
                for th in list1:
                    th.join()

            print('sending acknowledgement to', address)
            for obj in self.list_of_objects:
                return_list.append(json.loads(obj.to_json()))
            self.filtering(return_list, request["filter"])
            json_string = json.dumps(return_list)
            conn.send(json_string.encode())
            return True

    def handle_multicast(self):
        print("Starting multicast " + self.name)
        # print("List ".join(self.list_of_objects))
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
            data = json.loads(data.decode())
            resp_address = (data['ip_address'], data['port'])
            print('sending back to', address)
            node_info = Object()
            node_info.ip_address = self.ip_address
            node_info.port = self.port
            node_info.links = self.connected_ports
            node_info = node_info.to_json()
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.sendto(node_info.encode(), resp_address)

    def run(self):
        hm = threading.Thread(name='handle_multicast', target=self.handle_multicast)
        hm.start()
        htcp = threading.Thread(name='handle_tcp', target=self.handle_tcp)
        htcp.start()
