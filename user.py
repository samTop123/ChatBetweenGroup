import tkinter as tk
from tkinter import Tk, Text, Label, Button, END, NORMAL, DISABLED
from tkinter.scrolledtext import ScrolledText
import client
import constants
import socket
import threading
import sys

def end_program(root : Tk, client : socket.socket) -> None:
    client.send("[quit]".encode("utf-8"))
    root.destroy()
    client.close()
    sys.exit()

def send_message(client_used : socket.socket) -> None:
    message = writing_text.get("1.0", END).strip().replace("\n", "")
    if message:
        client_used.send(message.encode("utf-8"))
        reading_text.config(state=NORMAL)
        reading_text.insert(END, f"You: {message}\n")
        reading_text.config(state=DISABLED)
        writing_text.delete("1.0", END)

def get_message(client : socket.socket) -> None:
    while True:
        try:
            msg = client.recv(constants.BUFFER_SIZE).decode("utf-8")
            if msg:
                reading_text.config(state=NORMAL)
                reading_text.insert(END, f"Other: {msg}\n")
                reading_text.config(state=DISABLED)
        except:
            print("The connection was lost !")
            break

def initialize_message_area() -> None:
    messages_thread = threading.Thread(target=get_message, args=(client_used,))
    messages_thread.start()

if __name__ == "__main__":
    client_used = client.create_client()
    client_used.connect((constants.IP, constants.PORT))

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

    send_button = Button(root, text = "Send", command= lambda: send_message(client_used))

    exit_button = Button(root, text = "Exit", command = lambda: end_program(root, client_used))

    writingLabel.pack()
    writing_text.pack()

    readingLabel.pack()
    reading_text.pack()

    send_button.pack()
    exit_button.pack()

    initialize_message_area()

    tk.mainloop()