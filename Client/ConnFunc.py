import base64 
from CryptoFunc import *

def crypto_key_exchange(conn, public_key):
    encoded_pub = base64.b64encode(public_key) #base64 encode pub key
    send_data(conn, encoded_pub)
    server_pub = base64.b64decode(receive_data(conn))
    print(server_pub)
    return server_pub

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
            
            return full_data
        full_data += data

def send_data(conn, data):
    EOT_MESSAGE = b'<<EOT>>'
    data_lst = pad_bytes(data)
    for data in data_lst:
        conn.send(data)
    conn.send(pad_bytes(EOT_MESSAGE)[0])
    

