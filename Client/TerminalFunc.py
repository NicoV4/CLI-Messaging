import shutil
import time
import CryptoFunc
import Client.ConnFunc
import threading
import tty
import sys
import os
#import termios
#import msvcrt

class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'

def terminal_color():
    while True:
        ask_color = str(input("1) Blue\n2) Green\n3) Cyan\n4) Red\n5) Purple\n6) yellow\n7) White\nTerminal color: "))
        match ask_color:
            case "1":
                return bcolors.BLUE
            case "2":
                return bcolors.GREEN
            case "3":
                return bcolors.CYAN
            case "4":
                return bcolors.RED
            case "5":
                return bcolors.PURPLE
            case "6":
                return bcolors.YELLOW
            case "7":
                return bcolors.WHITE
            
def select_username(conn, private_key, public_key):
    while True:
        username = input("username: ") #get username from user
        
        Client.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, username))
        error_message = CryptoFunc.decrypt_data(private_key, Client.ConnFunc.receive_data(conn)).decode()
        if error_message == 'USERNAME OK':
            print("username ok")
            return username
        else:
            print(error_message)

def chat(conn, private_key, public_key):
    prev_msg = ""
    threading.Thread(target=user_input_linux, args=(conn, public_key)).start()
    while True:
        Client.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, "req")) #request chat
        all_msg = CryptoFunc.decrypt_data(private_key, Client.ConnFunc.receive_data(conn)).decode() #receive all messages
        if prev_msg != all_msg:
            os.system("clear")
            print(all_msg)
        prev_msg = all_msg
        time.sleep(0.5)

def update_input(user_input_list):
    try:
        width, height = shutil.get_terminal_size() #get width and height of terminal
    except shutil.Error:
        width = 80 #if fail set width manualy
    max_input_length = width - len(f"Send: ")
    truncated_input = "".join(user_input_list)[-max_input_length:]
    print("\rSend: " + (" " * max_input_length), end="\r")
    print(f"Send: {truncated_input}", end="\r")

def user_input_linux(conn, public_key):
    user_input_list = []
    while True:
        tty.setcbreak(sys.stdin.fileno())
        key = sys.stdin.read(1)
        if key:
            if key == '\x7f' or key == '\x08':  # Backspace
                if user_input_list:
                    user_input_list.pop()
                    update_input(user_input_list)
            elif key == '\n':
                user_input_str = "".join(user_input_list)
                if user_input_str:
                    Client.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, user_input_str))
                    user_input_list = []  # Clear the input list
            else:
                if len("".join(user_input_list)) < 750:
                    user_input_list.append(key)
                    update_input(user_input_list)
        time.sleep(0.01)

def user_input_windows(conn, server_public_key, fernet):
    global user_input_list, user_input_str
    while not exit_p:
        if msvcrt.kbhit(): #if input
            user_input = msvcrt.getwch() #get key
            if user_input == "\x08":  #if backspace pressed
                if user_input_list: #if list not empty
                    user_input_list.pop() #remove last character from input list
                    update_input()
            elif user_input == "\r": #if enter key is pressed
                if user_input_list: #if input is not empty
                    user_input_str = "".join(user_input_list) #join list to string
                    commands(user_input_str, conn, fernet)
                    user_input_list = []
            elif len(user_input_list) < 750: #if the input is less than 500 characters
                user_input_list.append(user_input) #add key to list
                update_input()
        time.sleep(0.0001)
    conn.close()
    print(bcolors.WHITE + "closed connection")

def check_window_focus_windows():
    global window_focus
    executable_path = os.path.abspath(sys.argv[0])
    executable_dir = os.path.dirname(executable_path)
    executable_filename = os.path.basename(executable_path)
    target_window_title = f'{executable_dir}\\{executable_filename}'
    while not exit_p:
        active_window = gw.getActiveWindow()
        if active_window and active_window.title == target_window_title:
            window_focus = True
        else:
            window_focus = False
        time.sleep(0.001)