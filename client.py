import socket
import ssl
import constants
import info_for_signature

class Client(object):
    @staticmethod
    def create_client() -> socket.socket:
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    @staticmethod
    def secure_client_socket(socket_client : socket.socket) -> ssl.SSLSocket:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_verify_locations(info_for_signature.SERVER_CERT_NAME)

        secured_client = context.wrap_socket(socket_client, server_hostname=constants.SERVER_HOST_NAME)

        return secured_client