import socket
import constants
from threading import Thread

def create_server() -> socket.socket:
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def handle_client(client_socket: socket.socket, other_client_socket: socket.socket) -> None:
    while True:
        try:
            msg = client_socket.recv(constants.BUFFER_SIZE)
            if msg == "[quit]":
                client_socket.close()
                other_client_socket.close()
                break
            if msg:
                other_client_socket.send(msg)
        except:
            print("The connection was lost !")
            break

if __name__ == "__main__":
    server = create_server()

    server.bind((constants.IP, constants.PORT))
    print("Waiting for clients...")

    server.listen(constants.MAX_CONNECTIONS)
    
    conn1, addr1 = server.accept()

    print("User 1 : ")
    print(addr1)

    conn1.send("Hello User 1".encode("utf-8"))

    conn2, addr2 = server.accept()

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