import base64
import Server.RoomsFunc
import ConnFunc
import CryptoFunc

def listener(conn, addr, private_key, public_key, rooms_list, create_room_allow, sym_key):
    print(f"received conn from... {addr}")
    client_pub = base64.b64decode(ConnFunc.receive_data(conn))
    encoded_pub = base64.b64encode(public_key) #base64 encode pub key
    ConnFunc.send_data(conn, encoded_pub)
    ser_client_pub = CryptoFunc.serialize_pub(client_pub)
    print(client_pub)
    
    username = Server.RoomsFunc.username_checker(conn, private_key, ser_client_pub)
    print(username)

    ConnFunc.send_data(conn, CryptoFunc.encrypt_data_asym(ser_client_pub, base64.b64encode(sym_key).decode())) #send symmetric key

    while True:
        data = ConnFunc.recv_sym_data(conn, sym_key)
        print(data)
        
        if data == b"list": #user requests for list of rooms
            print("sending rooms...")
            print(str(list(rooms_list)).encode())
            room_name_lst = []
            for room in rooms_list:
                room_name_lst.append(f"»{room[0]}")
            ConnFunc.send_sym_data(conn, sym_key, "\t".join(room_name_lst))
        
        elif data[:len(b"create")] == b"create":
            if len(data) > len(b"create"): #check if room name after "create"
                room_name = data[len(b"create")+1:] #save room name to var
                print(room_name)
                Server.RoomsFunc.create_room(conn, sym_key, create_room_allow, rooms_list, room_name.decode())
            else:
                ConnFunc.send_sym_data(conn, sym_key, "No room name specified")
        
        elif data[:len(b"info")] == b"info":
            if len(data) > len(b"info"): #check if room name after "info"
                room_name = data[len(b"info")+1:].decode() #save room name to var
                Server.RoomsFunc.room_info(conn, sym_key, rooms_list, room_name)
            else:
                ConnFunc.send_sym_data(conn, sym_key, "No room name specified")
                
        elif data[:len(b"connect")] == b"connect":
            if len(data) > len(b"connect"):
                room_name = data[len(b"connect")+1:].decode()
                Server.RoomsFunc.connect_room(conn, sym_key, rooms_list, room_name, username, private_key)
            else:
                ConnFunc.send_sym_data(conn, sym_key, "No room name specified")
        
        elif data == b"help":
            help = """
create {room name}          |\tTell server to create a room
exit                        |\tExit program
list                        |\tRequest server list of all rooms
help                        |\tList all possible commands
connect {room name}         |\tRequest to connect to room
info {room name}            |\tGet info about room
"""
            ConnFunc.send_sym_data(conn, sym_key, help)
        
        else:
            ConnFunc.send_sym_data(conn, sym_key, "Invalid command")
            
        if not data:
            conn.close() #end socket if connection closed
            return