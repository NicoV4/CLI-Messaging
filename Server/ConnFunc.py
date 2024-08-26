import base64
import CryptoFunc
import Server.ConnFunc
import Server.RoomsFunc
chunk_size = 256

def crypto_key_exchange(conn, public_key):
    client_pub = base64.b64decode(receive_data(conn))
    print(client_pub)
    encoded_pub = base64.b64encode(public_key) #base64 encode pub key
    send_data(conn, encoded_pub)
    return client_pub

def send_data(conn, data):
    EOT_MESSAGE = b'<<EOT>>'
    data_lst = pad_bytes(data)
    for data in data_lst:
        conn.send(data)
    conn.send(pad_bytes(EOT_MESSAGE)[0])

def receive_data(conn):
    EOT_MESSAGE = b'<<EOT>>'
    BUFFER_SIZE = 256
    full_data = b""
    while True:
        data = conn.recv(BUFFER_SIZE).rstrip(b'\x00')
        
        if not data:
            conn.close()
            return
        elif data == EOT_MESSAGE:
            
            print("eot found")
            return full_data
        full_data += data

def pad_bytes(data):
    chunk_size = 256
    splt_data = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)] #splite data into correct chunks
    data_list = []
    for data in splt_data:
        try:
            byte_data = data.encode('utf-8') # Convert the string to bytes
        except AttributeError:
            byte_data = data
            pass

        if len(byte_data) < chunk_size: 
            byte_data = byte_data.ljust(chunk_size, b'\x00') # Pad the byte array with spaces (0x20) or null bytes (0x00) if it is too short
        else:
            byte_data = byte_data[:chunk_size] # Truncate the byte array if it is too long
        data_list.append(byte_data) #save all messages to list
    return data_list #return list

def username_checker(conn, private_key, public_key):
    while True:
        username = CryptoFunc.decrypt_data(private_key, receive_data(conn)).decode()
        print(username)
        if len(username) < 3 or len(username) > 25: #if username is less then 3 or more than 25 bad
            print("bad length")
            send_data(conn, CryptoFunc.encrypt_data(public_key, "username needs to be between 3 and 25 characters"))
        else:
            print("ok")
            send_data(conn, CryptoFunc.encrypt_data(public_key, "USERNAME OK"))
            return username
        
def listener(conn, addr, private_key, public_key, rooms_list, create_room_allow):
    print(f"received conn from... {addr}")
    
    client_pub = CryptoFunc.serialize_pub(crypto_key_exchange(conn, public_key))
    print(client_pub)
    
    username = username_checker(conn, private_key, client_pub)
    print(username)
    
    while True:
        data = CryptoFunc.decrypt_data(private_key, receive_data(conn))
        print(data)
        
        if data == b"list": #user requests for list of rooms
            print("sending rooms...")
            print(str(list(rooms_list)).encode())
            send_data(conn, CryptoFunc.encrypt_data(client_pub, str(list(rooms_list))))
        
        elif data[:len(b"create")] == b"create":
            if len(data) > len(b"create"):
                room_name = data[len(b"create")+1:]
                print(room_name)
                Server.RoomsFunc.create_room(conn, client_pub, create_room_allow, rooms_list, room_name.decode())
            else:
                send_data(conn, CryptoFunc.encrypt_data(client_pub, "No room name specified"))
        
        elif data[:len(b"connect")] == b"connect":
            room_name = data[len(b"connect")+1:].decode()
            Server.RoomsFunc.connect_room(conn, client_pub, rooms_list, room_name, username, private_key)
        
        elif data == b"help":
            help = """
create\t|\tCreate a room
exit  \t|\tExit program
list  \t|\tList rooms
help  \t|\tList all possible commands
"""
            send_data(conn, CryptoFunc.encrypt_data(client_pub, help))
        
        else:
            send_data(conn, CryptoFunc.encrypt_data(client_pub, "Invalid command"))
            
        if not data:
            conn.close() #end socket if connection closed
            return