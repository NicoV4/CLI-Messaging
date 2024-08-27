import re
import CryptoFunc
import ConnFunc
import time

def check_special_char(string):
    pattern = re.compile(r'^[a-zA-Z0-9 ]*$')
    # Check if the string matches the pattern
    return bool(pattern.match(string))

def create_room(conn, sym_key, create_allow, rooms_list, room_name):
    if create_allow:
        if not room_name:
            ConnFunc.send_sym_data(conn, sym_key, "No room name specified")
        if room_name:
            for room in rooms_list:
                if room[0] == room_name:
                    ConnFunc.send_sym_data(conn, sym_key, "Room already exists")
                    return
            if len(room_name) < 4:
                ConnFunc.send_sym_data(conn, sym_key, "Room name cannot be smaller than 4 characters")
            elif len(room_name) > 20:
                ConnFunc.send_sym_data(conn, sym_key, "Room name cannot be larger than 20 characters")
            elif not check_special_char(room_name):
                ConnFunc.send_sym_data(conn, sym_key, "Room name cannot contain special characters")
            else:
                rooms_list.append([room_name, [], []]) #[[room name], [usernames], [messages]]
                ConnFunc.send_sym_data(conn, sym_key, f"CREATED ROOM: {room_name}")
    else:
        ConnFunc.send_sym_data(conn, sym_key, "Room creation is not allowed at this time")

def chat(conn, sym_key, private_key, room, username):
    print(f"{username} connected to room")
    while True:
        msg = ConnFunc.receive_data(conn) #get message from client
        try:
            num_req = int(msg.decode()) #try to decrypt asym and convert to int
            print(num_req)
            print(f"len: {len(room[2])}")
            print(room[2])
            if len(room[2])-1 >= num_req: #check if requested message
                ConnFunc.send_sym_data(conn, sym_key, room[2][num_req]) #send requested message
            else:
                ConnFunc.send_sym_data(conn, sym_key, "None") #if message doesn't exist yet send plain text "None"
        except Exception as e:
            print(e)
            try:
                iv = msg
                chat_msg = ConnFunc.receive_data(conn) #get sym encrypted message
                msg = CryptoFunc.decrypt_data_sym(sym_key, iv, chat_msg) #if cannot convert to int try to decrypt message
                print(msg)
                room[2].append(f"{username}> {msg.decode()}") #add message to message list
            except Exception as e:
                print(e)
                pass

        print(room)
        time.sleep(0.1)

def username_checker(conn, private_key, public_key):
    while True:
        username = CryptoFunc.decrypt_data_asym(private_key, ConnFunc.receive_data(conn)).decode()
        print(username)
        if len(username) < 3 or len(username) > 25: #if username is less then 3 or more than 25 bad
            print("bad length")
            ConnFunc.send_data(conn, CryptoFunc.encrypt_data_asym(public_key, "username needs to be between 3 and 25 characters"))
        else:
            print("ok")
            ConnFunc.send_data(conn, CryptoFunc.encrypt_data_asym(public_key, "USERNAME OK"))
            return username

def connect_room(conn, sym_key, rooms_list, room_name, username, private_key):
    print(len(rooms_list))
    for i in range(len(rooms_list)): #loop through list with rooms
        print(rooms_list[i][0])
        if room_name == rooms_list[i][0]: #if the room name is found in the list
            rooms_list[i][1].append(username) #add user to room
            ConnFunc.send_sym_data(conn, sym_key, f"Connected to room {room_name}")
            chat(conn, sym_key, private_key, rooms_list[i], username)
            return
    ConnFunc.send_sym_data(conn, sym_key, f"Room {room_name} does not exist")
        
def room_info(conn, sym_key, rooms_list, room_name):
    for i in range(len(rooms_list)): #loop through list of rooms
        if rooms_list[i][0] == room_name: #if room name found
            if len(rooms_list[i][1]) > 0: #check if empty room
                users_lst = []
                for user in rooms_list[i][1]:
                    users_lst.append(f"»{user}")
                    ConnFunc.send_sym_data(conn, sym_key, "\n".join(users_lst)) #send list of users
                    return
            elif len(rooms_list[i][1]) == 0:
                ConnFunc.send_sym_data(conn, sym_key, "Room is empty") #send room empty if empty
                return
    ConnFunc.send_sym_data(conn, sym_key, "Room not found") #if no room found
    return