import re
import CryptoFunc
import Server.ConnFunc
import time

def check_special_char(string):
    pattern = re.compile(r'^[a-zA-Z0-9 ]*$')
    # Check if the string matches the pattern
    return bool(pattern.match(string))

def create_room(conn, public_key, create_allow, rooms_list, room_name):
    if create_allow:
        if not room_name:
            Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, "No room name specified"))
        if room_name:
            while True:
                if len(room_name) < 4:
                    Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, "Room name cannot be smaller than 4 characters"))
                elif len(room_name) > 20:
                    Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, "Room name cannot be larger than 20 characters"))
                elif not check_special_char(room_name):
                    Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, "Room name cannot contain special characters"))
                else:
                    rooms_list.append([[room_name], [], []]) #[[room name], [usernames], [messages]]
                    Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, f"CREATED ROOM: {room_name}"))
                    return
    else:
        Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, "Room creation is not allowed at this time"))

def chat(conn, public_key, private_key, room, username):
    while True:
        chat_msg = CryptoFunc.decrypt_data(private_key, Server.ConnFunc.receive_data(conn)).decode() #get chat message from client
        if chat_msg == "req":
            Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, "\n".join(room[2])))
        else:
            Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, f"recv"))
            room[2].append(f"{username}> {chat_msg}")
        print(room)
        time.sleep(0.5)


def connect_room(conn, public_key, rooms_list, room_name, username, private_key):
    print(rooms_list)
    for room in rooms_list: #loop through list with rooms
        print(room)
        if room_name in room[0]: #if the room name is found in the list
            room[1].append(username) #add user to room
            print(room)
            Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, f"Connected to room {room_name}"))
            chat(conn, public_key, private_key, room, username)
        elif not room_name in room[0]:
            Server.ConnFunc.send_data(conn, CryptoFunc.encrypt_data(public_key, f"Room {room_name} does not exists"))