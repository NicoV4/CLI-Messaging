import os
import platform
import shutil
import time
import CryptoFunc
import ConnFunc
import threading
if platform.system() == "Linux":
    import tty
elif platform.system() == "Windows":
    import msvcrt
import sys

#import termios

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
        
        ConnFunc.send_data(conn, CryptoFunc.encrypt_data_asym(public_key, username))
        error_message = CryptoFunc.decrypt_data_asym(private_key, ConnFunc.receive_data(conn)).decode()
        if error_message == 'USERNAME OK':
            print("username ok")
            return username
        else:
            print(error_message)

def chat(conn, username, sym_key):
    msg_num = 0
    if platform.system() == "Linnux":
        threading.Thread(target=user_input_linux, args=(conn, sym_key, username)).start() #start thread for input
    elif platform.system() == "Windows":
         threading.Thread(target=user_input_windows, args=(conn, sym_key, username)).start() #start thread for input
    while True:
        ConnFunc.send_data(conn, str(msg_num)) #request msg number
        try:
            #HALF BROKEN, will fix later
            recv_message = ConnFunc.recv_sym_data(conn, sym_key) #receive requested message
        except Exception as e:
            recv_message = b"None"
        if recv_message == b"None":
            continue #if message "None" do nothing
        else:
            print(recv_message.decode()) #print received message
            msg_num += 1
        time.sleep(0.25)

def update_input(user_input_list, username):
    try:
        width, height = shutil.get_terminal_size() #get width and height of terminal
    except shutil.Error:
        width = 80 #if fail set width manualy
    max_input_length = width - len(f"{username}> ")
    if platform.system() == "Linux":
        truncated_input = "".join(user_input_list)[-max_input_length:]
    elif platform.system() == "Windows":
        max_input_length-=2
        truncated_input = "".join(user_input_list)[-max_input_length:]
    print("\r" + f"{username}> " + (" " * max_input_length), end="\r")
    print(f"{username}> {truncated_input}", end="\r")

def user_input_linux(conn, sym_key, username):
    user_input_list = []
    while True:
        tty.setcbreak(sys.stdin.fileno())
        key = sys.stdin.read(1)
        if key:
            if key == '\x7f' or key == '\x08':  #if backspace pressed
                if user_input_list:
                    user_input_list.pop() #remove last char from list
                    update_input(user_input_list, username) #update cli
            elif key == '\n': # if enter pressed
                user_input_str = "".join(user_input_list) #convert list to string
                if user_input_str: #if not empty
                    ConnFunc.send_sym_data(conn, sym_key, user_input_str) #send string to server
                    user_input_list = []  # Clear the input list
                    update_input(user_input_list, username)
                    #print(" " * len(f"{username}> " + user_input_str), end="\r") #clear line
            else:
                if len("".join(user_input_list)) < 750: #check if input is under the limit
                    user_input_list.append(key)
                    update_input(user_input_list, username)
        time.sleep(0.01)
        
def user_input_windows(conn, sym_key, username):
    user_input_list = []
    while True:
        if msvcrt.kbhit(): #if input
            key = msvcrt.getwch() #get key
            if key == '\x08':  #if backspace pressed
                if user_input_list:
                    user_input_list.pop() #remove last char from list
                    update_input(user_input_list, username) #update cli
            elif key == '\r': # if enter pressed
                user_input_str = "".join(user_input_list) #convert list to string
                if user_input_str: #if not empty
                    ConnFunc.send_sym_data(conn, sym_key, user_input_str) #send string to server
                    user_input_list = []  # Clear the input list
                    update_input(user_input_list, username)
                    #print(" " * len(f"{username}> " + user_input_str), end="\r") #clear line
                    
            else:
                if len("".join(user_input_list)) < 750: #check if input is under the limit
                    user_input_list.append(key)
                    update_input(user_input_list, username)
        time.sleep(0.01)

#needs fixing
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