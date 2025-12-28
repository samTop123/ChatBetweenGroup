import socket

def create_client() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)