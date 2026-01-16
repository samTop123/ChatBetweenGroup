import tkinter as tk
from tkinter import Tk, Text, Label, Button, END, NORMAL, DISABLED
from tkinter.scrolledtext import ScrolledText
import info_for_signature
from client import Client
import constants
import socket
import threading
import sys
import ssl

class ClientApp(object):
    def __init__(self, root: Tk, client_socket: ssl.SSLSocket):
        self.root = root
        self.client_socket = client_socket

    def end_program(self) -> None:
        self.client_socket.send("[quit]".encode("utf-8"))
        self.root.destroy()
        self.client_socket.close()
        sys.exit()

    def send_message(self, client_name : str, writing_text : Text, reading_text : Text) -> None:
        message = writing_text.get("1.0", END).strip().replace("\n", "")

        if message:
            message = f"{client_name}:{message}"
            self.client_socket.send(message.encode("utf-8"))
            self.append_text(reading_text, f"{message}\n")
            writing_text.delete("1.0", END)

    def append_text(self, reading_text : Text, text : str) -> None:
        reading_text.config(state=NORMAL)
        reading_text.insert(END, text)
        reading_text.config(state=DISABLED)

    def get_message(self, reading_text : Text) -> None:
        while True:
            try:
                msg = self.client_socket.recv(constants.BUFFER_SIZE).decode("utf-8")
                if msg:
                    username_other, message = msg.split(":", 1)  # split at first colon only
                    self.root.after(0, self.append_text, reading_text, f"{username_other}:{message}\n")
            except Exception as e:
                print(f"The connection was lost : {e} !")
                break

    def initialize_message_area(self, reading_text : Text) -> None:
        messages_thread = threading.Thread(target=self.get_message, args=(reading_text, ), daemon=True)
        messages_thread.start()

def reset_username(username_text_widget : Text, first_username : str) -> None:
    username_text_widget.delete("1.0", END)
    username_text_widget.insert(END, first_username)

def initialize_app(root : Tk, client_app : ClientApp) -> tuple[Text, ScrolledText, Text]:
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

    send_button = Button(root, text = "Send", command= lambda: client_app.send_message(username_text.get("1.0", END).strip().replace("\n", ""), writing_text, reading_text))

    exit_button = Button(root, text = "Exit", command = lambda: client_app.end_program())

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

    return (writing_text, reading_text, username_text)

if __name__ == "__main__":
    client_used = Client.create_client()
    client_secured_used = Client.secure_client_socket(client_used)
    client_secured_used.connect((constants.IP, constants.PORT))
    client_secured_used.send(b"[ready]")

    # Displaying the cipher information - (algorithm used for symmetric encryption, TLS version, Key length - in bits)
    print(client_secured_used.cipher())

    root = Tk()
    client_app = ClientApp(root, client_secured_used)

    writing_text, reading_text, username_text = initialize_app(root, client_app)

    client_app.initialize_message_area(reading_text)

    tk.mainloop()