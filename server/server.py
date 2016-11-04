import pickle
from settings import server_name, server_port
import threading
import logging
from socket import socket as Socket

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(message)s')

urls = [
    "http://google.com", "http://youtube.com", "http://yandex.ru", "https://www.crummy.com/", "https://pymotw.com",
    "https://www.analyticsvidhya.com", "http://stackoverflow.com/",
]

parsed_urls = {'urls': []}
buff = bytes()


class Server:
    def __init__(self, server_address, server_port, max_connections):
        self.socket = Socket()
        self.address = server_address
        self.port = server_port
        self.connections = max_connections

    def start(self):
        logging.info('Starting server')
        self.socket.bind((self.address, self.port))
        self.socket.listen(self.connections)
        logging.info('Server has been started. Waiting for connections.')

    def close(self):
        self.socket.close()

    def accept(self):
        client_sock, client_addr = self.socket.accept()
        return client_sock, client_addr

    def receive(self, buffer_size):
        return self.socket.recv(buffer_size)

    def send(self, data, flags=0):
        return self.socket.send(data, flags)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.__exit__(exc_type, exc_val, exc_tb)
        logging.info('Server closed')

    @staticmethod
    def provide_client_tasks(client_conn):
        logging.debug('Starting new thread')
        with client_conn:
            while True:
                response = pickle.loads(client_conn.receive(65536))
                logging.debug('Client response: {response}'.format(response=response))

                if response.get('new_task') and urls:
                    logging.debug('Sending new task')
                    client_conn.send(pickle.dumps(
                        {'url': urls.pop(), }
                    ))

                elif response.get('url'):
                    logging.debug("Got new task:" + str(response))
                    parsed_urls['urls'].append(response['url'])
                    logging.debug("New parsed urls file" + str(parsed_urls))

                else:
                    client_conn.send(pickle.dumps(
                        {'done': True, }
                    ))
                    logging.debug('Exiting')
                    break


class Client:
    def __init__(self, client_socket, client_address):
        self.socket = client_socket
        self.address = client_address

    def send(self, data, flags=0):
        return self.socket.send(data, flags)

    def receive(self, buff_size):
        return self.socket.recv(buff_size)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.socket.__exit__(exc_type, exc_val, exc_tb)


with Server(server_name, server_port, max_connections=10) as server:
    server.start()

    while True:
        client = Client(*server.accept())
        threading.Thread(target=server.provide_client_tasks, args=(client,)).start()