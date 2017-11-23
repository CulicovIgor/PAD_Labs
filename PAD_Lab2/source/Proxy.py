import json
import socket
import uuid
import dicttoxml
import threading
from source.data.data_creator import Object
from source.node.node import Node


class Proxy:
    def __init__(self):
        self.collected_data = []
        self.IP_ADDRESS = '127.0.0.1'
        self.PORT = 9099

        # multicast group
        print("Create multicast socket")
        self.multicast_group = ('224.3.29.71', 10000)
        self.multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.multicast_socket.settimeout(1)
        self.multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

        # node response socket
        print("Create socket for nodes\n")
        self.server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_udp.settimeout(1)
        self.server_udp.bind((self.IP_ADDRESS, self.PORT))
        """
        start_conf = json.loads(open('startup_conf.json', 'r').read())
        list_of_nodes = []
        for node in start_conf:
            thread = Node(node['name'], node['port'], node['connected_ports'])
            list_of_nodes.append(thread)
        for thread in list_of_nodes:
            thread.start()"""

    def get_conn_socket_data(self, ip, port, msg, collected_data):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(msg.encode())
        data = s.recv(1024)
        if data.decode() == '':
            s.close()
        else:
            data = json.loads(data.decode())
            for obj in data:
                collected_data.append(obj)
            s.close()

    def run(self):
        # tcp socket
        print("Create socket for clients\n")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.IP_ADDRESS, self.PORT))
        server.listen()

        while True:
            print('\nwaiting client message')
            conn, address = server.accept()
            thread = threading.Thread(name='handle_client_request', target=self.handle_client_request,
                                      args=(conn, address))
            thread.start()

    def handle_client_request(self, conn, address):
        request = conn.recv(1024)
        request = json.loads(request.decode())
        mc_message = Object()
        mc_message.ip_address = self.IP_ADDRESS
        mc_message.port = self.PORT
        mc_message = mc_message.to_json()
        # Send data to the multicast group
        print('sending "%s"' % mc_message)

        self.multicast_socket.sendto(mc_message.encode(), self.multicast_group)
        answer_list = []
        visit_ports = []
        stored_ports = []
        # Receive multicast answer
        try:
            while True:
                data, addr = self.server_udp.recvfrom(1024)
                answer_list.append(json.loads(data.decode()))
        except socket.timeout:
            pass
        answer_list = sorted(answer_list, key=lambda node: len(node['links']), reverse=True)
        print(answer_list)
        for node in answer_list:
            print(stored_ports)
            if node['port'] not in stored_ports:
                print("ADD port %s" % node['port'])
                visit_ports.append(node)
                stored_ports.append(node['port'])
                for connected in node['links']:
                    print("Connected %s" % connected)
                    if connected not in stored_ports:
                        stored_ports.append(connected)
        # tcp to nodes for data
        MESSAGE = Object()
        MESSAGE.uuid = uuid.uuid4().hex
        MESSAGE.depth = 1
        MESSAGE.type = "data"
        MESSAGE.filter = request['filter']
        MESSAGE = MESSAGE.to_json()
        list1 = []
        collected_data = []
        for node in visit_ports:
            thread = threading.Thread(name='get_conn_socket_data', target=self.get_conn_socket_data,
                                      args=('127.0.0.1', node['port'], MESSAGE, collected_data))
            thread.start()
            list1.append(thread)
        for th in list1:
            th.join()
        if request['type'] == 'xml':
            xml = dicttoxml.dicttoxml(collected_data)
            conn.send(xml)
        else:
            conn.send(json.dumps(collected_data).encode())
        return True


if __name__ == '__main__':
    proxy = Proxy()
    proxy.run()
