import logging
import pickle
from settings import server_name, server_port
from socket import socket as Socket
from utils.html_parser import UrlParser
import sys

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] %(message)s',
                    )

logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(message)s')


def unpickle_response(response):
    return pickle.loads(response)


def ask_for_task(socket):
    return socket.sendall(pickle.dumps({'new_task': True}))


def get_response_from(socket):
    return socket.recv(2048)


logging.info('Starting client')
with Socket() as client_socket:
    client_socket.connect((server_name, server_port))
    logging.info('Connected')

    while True:
        ask_for_task(client_socket)
        server_response = unpickle_response(get_response_from(client_socket))

        # if server_response.get('url'):
        #     print(str(server_response))

        url = server_response.pop('url', None)

        if url:
            logging.debug("Got url: {url}".format(url=url))
            parsed_url = UrlParser(url)
            url_title = parsed_url.get_title()
            url_links = parsed_url.get_links()

            data = {
                    'url': url,
                    'title': url_title,
                    'links': url_links,
                }

            print(sys.getsizeof(pickle.dumps(data)))

            client_socket.sendall(pickle.dumps(data))

        elif server_response.get("done"):
            client_socket.close()
            logging.debug("Socket has been closed")
            break

