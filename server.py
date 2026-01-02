import ssl
import socket
import constants
import generating_key
import info_for_signature
from threading import Thread

def create_server() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handle_client(client_socket: ssl.SSLSocket, other_client_socket: ssl.SSLSocket) -> None:
    while True:
        try:
            msg = client_socket.recv(constants.BUFFER_SIZE)
            if msg == b"[quit]":
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
                break
            if msg:
                other_client_socket.send(msg)
        except:
            print("The connection was lost !")
            break

def secure_server_socket(server_socket : socket.socket) -> ssl.SSLSocket:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    
    if not generating_key.files_are_init():
        generating_key.create_key_and_certificate()

    context.load_cert_chain(certfile=info_for_signature.SERVER_CERT_NAME, keyfile=info_for_signature.SERVER_KEY_NAME_PRIVATE)

    secured_server = context.wrap_socket(server_socket, server_side=True)

    return secured_server

if __name__ == "__main__":
    server = create_server()

    server.bind((constants.IP, constants.PORT))

    print("Waiting for clients...")

    server.listen(constants.MAX_CONNECTIONS)
    secured_server = secure_server_socket(server)
    conn1, addr1 = secured_server.accept()

    print("User 1 : ")
    print(addr1)

    conn1.send("Hello User 1".encode("utf-8"))

    conn2, addr2 = secured_server.accept()

    print("User 2 : ")
    print(addr2)

    conn2.send("Hello User 2".encode("utf-8"))

    try:
        thread1 = Thread(target=handle_client, args=(conn1, conn2))
        thread2 = Thread(target=handle_client, args=(conn2, conn1))

        thread1.start()
        thread2.start()
    except:
        print("The connection was lost !")