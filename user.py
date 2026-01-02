import tkinter as tk
from tkinter import Tk, Text, Label, Button, END, NORMAL, DISABLED
from tkinter.scrolledtext import ScrolledText
import info_for_signature
import client
import constants
import socket
import threading
import sys
import ssl

def end_program(root : Tk, client : ssl.SSLSocket) -> None:
    client.send("[quit]".encode("utf-8"))
    root.destroy()
    client.close()
    sys.exit()

def send_message(client_used : ssl.SSLSocket) -> None:
    message = writing_text.get("1.0", END).strip().replace("\n", "")
    if message:
        client_used.send(message.encode("utf-8"))
        reading_text.config(state=NORMAL)
        reading_text.insert(END, f"You: {message}\n")
        reading_text.config(state=DISABLED)
        writing_text.delete("1.0", END)

def append_text(text):
    reading_text.config(state=NORMAL)
    reading_text.insert(END, text)
    reading_text.config(state=DISABLED)

def get_message(client : ssl.SSLSocket) -> None:
    while True:
        try:
            msg = client.recv(constants.BUFFER_SIZE).decode("utf-8")
            if msg:
                root.after(0, append_text, f"Other: {msg}\n")
        except:
            print("The connection was lost !")
            break

def initialize_message_area(client_used : ssl.SSLSocket) -> None:
    messages_thread = threading.Thread(target=get_message, args=(client_used,), daemon=True)
    messages_thread.start()

def secure_client_socket(socket_client : socket.socket) -> ssl.SSLSocket:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(info_for_signature.SERVER_CERT_NAME)

    secured_client = context.wrap_socket(socket_client, server_hostname="localhost")

    return secured_client

if __name__ == "__main__":
    client_used = client.create_client()
    client_secured_used = secure_client_socket(client_used)
    client_secured_used.connect((constants.IP, constants.PORT))

    root = Tk()

    # specify size of window.
    root.geometry("500x350")

    # Text widgets for writing and reading messages.
    writing_text = Text(root, height = 5, width = 52)
    reading_text = ScrolledText(root, height = 5, width = 52, state=DISABLED)

    # Labels for the text areas.
    writingLabel = Label(root, text = "Writing Area : ")
    writingLabel.config(font =("Courier", 14))

    readingLabel = Label(root, text = "Reading Area : ")
    readingLabel.config(font =("Courier", 14))

    send_button = Button(root, text = "Send", command= lambda: send_message(client_secured_used))

    exit_button = Button(root, text = "Exit", command = lambda: end_program(root, client_secured_used))

    writingLabel.pack()
    writing_text.pack()

    readingLabel.pack()
    reading_text.pack()

    send_button.pack()
    exit_button.pack()

    initialize_message_area(client_secured_used)

    tk.mainloop()