import ssl
import socket
import constants
import generating_key
import info_for_signature
from threading import Thread

def create_server() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handle_client(clients_socket: list[ssl.SSLSocket], other_client_socket: ssl.SSLSocket) -> None:
    while True:
        try:
            msg = other_client_socket.recv(constants.BUFFER_SIZE)
            if msg == b"[quit]":
                other_client_socket.shutdown(socket.SHUT_RDWR)
                other_client_socket.close()
                break
            if msg:
                for client_socket in clients_socket:
                    if client_socket != other_client_socket:
                        client_socket.send(msg)
        except Exception as e:
            print(f"The connection was lost : {e} !")
            break

def secure_server_socket(server_socket : socket.socket) -> ssl.SSLSocket:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    if not generating_key.files_are_init():
        generating_key.create_key_and_certificate()

    context.load_cert_chain(certfile=info_for_signature.SERVER_CERT_NAME, keyfile=info_for_signature.SERVER_KEY_NAME_PRIVATE)

    secured_server = context.wrap_socket(server_socket, server_side=True)

    return secured_server

if __name__ == "__main__":
    users = []
    threads = []

    server = create_server()

    server.bind((constants.IP, constants.PORT))

    print("Waiting for clients...")

    server.listen(constants.MAX_CONNECTIONS)
    secured_server = secure_server_socket(server)

    while len(users) < constants.MAX_CONNECTIONS:
        conn, addr = secured_server.accept()

        print(f"User {len(users)+1} : ")
        print(addr)

        conn.send(f"User {len(users)+1}".encode("utf-8"))

        conn.recv(constants.BUFFER_SIZE)  # Wait for user to be ready
        users.append(conn)

    try:
        for user in users:
            thread = Thread(target=handle_client, args=(users, user))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    except:
        print("The connection was lost !")