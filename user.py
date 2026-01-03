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

def send_message(client_name : str, client_used : ssl.SSLSocket) -> None:
    message = writing_text.get("1.0", END).strip().replace("\n", "")

    if message:
        message = f"{client_name}:{message}"
        client_used.send(message.encode("utf-8"))
        append_text(f"{message}\n")
        writing_text.delete("1.0", END)

def append_text(text : str) -> None:
    reading_text.config(state=NORMAL)
    reading_text.insert(END, text)
    reading_text.config(state=DISABLED)

def get_message(client : ssl.SSLSocket) -> None:
    while True:
        try:
            msg = client.recv(constants.BUFFER_SIZE).decode("utf-8")
            if msg:
                username_other, message = msg.split(":", 1)  # split at first colon only
                root.after(0, append_text, f"{username_other}:{message}\n")
        except Exception as e:
            print(f"The connection was lost : {e} !")
            break

def initialize_message_area(client_used : ssl.SSLSocket) -> None:
    messages_thread = threading.Thread(target=get_message, args=(client_used,), daemon=True)
    messages_thread.start()

def secure_client_socket(socket_client : socket.socket) -> ssl.SSLSocket:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(info_for_signature.SERVER_CERT_NAME)

    secured_client = context.wrap_socket(socket_client, server_hostname=constants.SERVER_HOST_NAME)

    return secured_client

def reset_username(username_text_widget : Text, first_username : str) -> None:
    username_text_widget.delete("1.0", END)
    username_text_widget.insert(END, first_username)

if __name__ == "__main__":
    client_used = client.create_client()
    client_secured_used = secure_client_socket(client_used)
    client_secured_used.connect((constants.IP, constants.PORT))
    client_secured_used.send(b"[ready]")

    # Displaying the cipher information - (algorithm used for symmetric encryption, TLS version, Key length - in bits)
    print(client_secured_used.cipher())

    root = Tk()

    # specify size of window.
    root.geometry("800x500")

    # Text widgets for writing and reading messages.
    writing_text = Text(root, height = 5, width = 52)
    reading_text = ScrolledText(root, height = 5, width = 52, state=DISABLED)

    first_username = client_secured_used.recv(constants.BUFFER_SIZE).decode("utf-8")

    username_text = Text(root, height = 1, width = 20)
    username_text.insert(END, first_username)

    username_label = Label(root, text = f"Connected as: ")
    username_label.config(font =("Courier", 14))

    # Labels for the text areas.
    writing_label = Label(root, text = "Writing Area : ")
    writing_label.config(font =("Courier", 14))

    reading_label = Label(root, text = "Reading Area : ")
    reading_label.config(font =("Courier", 14))

    send_button = Button(root, text = "Send", command= lambda: send_message(username_text.get("1.0", END).strip().replace("\n", ""), client_secured_used))

    exit_button = Button(root, text = "Exit", command = lambda: end_program(root, client_secured_used))

    reset_username_button = Button(root, text = "Reset Username", command = lambda: reset_username(username_text, first_username))

    username_label.pack()
    username_text.pack()
    reset_username_button.pack()

    reading_label.pack()
    reading_text.pack()

    writing_label.pack()
    writing_text.pack()

    send_button.pack()
    exit_button.pack()

    initialize_message_area(client_secured_used)

    tk.mainloop()