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
        """
        start_conf = json.loads(open('startup_conf.json', 'r').read())
        list_of_nodes = []
        for node in start_conf:
            thread = Node(node['name'], node['port'], node['connected_ports'])
            list_of_nodes.append(thread)
        for thread in list_of_nodes:
            thread.start()"""

    def get_conn_socket_data(self, ip, port, msg):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.send(msg.encode())
        data = s.recv(1024)
        if data.decode() == '':
            s.close()
        else:
            data = json.loads(data.decode())
            for obj in data:
                self.collected_data.append(obj)
            s.close()

    def run(self):
        IP_ADDRESS = '127.0.0.1'
        PORT = 9099
        BUFFER_SIZE = 1024
        # multicast group

        print("Create multicast socket")
        mc_message = Object()
        mc_message.ip_address = IP_ADDRESS
        mc_message.port = PORT
        mc_message = mc_message.to_json()
        multicast_group = ('224.3.29.71', 10000)
        multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        multicast_socket.settimeout(1)
        multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

        # tcp socket
        print("Create socket for clients\n")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((IP_ADDRESS, PORT))
        server.listen()

        # node response socket
        print("Create socket for nodes\n")
        server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_udp.settimeout(1)
        server_udp.bind((IP_ADDRESS, PORT))
        while True:
            print('\nwaiting client message')
            conn, address = server.accept()
            request = conn.recv(1024)
            request = json.loads(request.decode())
            # Send data to the multicast group
            print('sending "%s"' % mc_message)
            multicast_socket.sendto(mc_message.encode(), multicast_group)
            answer_list = []
            visit_ports = []
            stored_ports = []
            # Receive multicast answer
            try:
                while True:
                    data, addr = server_udp.recvfrom(1024)
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
            for node in visit_ports:
                thread = threading.Thread(name='get_conn_socket_data', target=self.get_conn_socket_data,
                                          args=('127.0.0.1', node['port'], MESSAGE))
                thread.start()
                list1.append(thread)
            for th in list1:
                th.join()
            if request['type'] == 'xml':
                xml = dicttoxml.dicttoxml(self.collected_data)
                conn.send(xml)
            else:
                conn.send(json.dumps(self.collected_data).encode())
            self.collected_data = []


if __name__ == '__main__':
    proxy = Proxy()
    proxy.run()
