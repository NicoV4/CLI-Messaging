import CryptoFunc

BUFFER_SIZE = 64

def send_data(conn, data):
    EOT_MESSAGE = b'<<EOT>>'
    data_lst = pad_bytes(data)
    for data in data_lst:
        conn.send(data)
    conn.send(pad_bytes(EOT_MESSAGE)[0])

def receive_data(conn):
    EOT_MESSAGE = b'<<EOT>>'
    
    full_data = b""
    while True:
        data = conn.recv(BUFFER_SIZE).rstrip(b'\x00')
        
        if not data:
            conn.close()
            return
        elif data == EOT_MESSAGE:
            return full_data
        
        full_data += data

def pad_bytes(data):
    splt_data = [data[i:i + BUFFER_SIZE] for i in range(0, len(data), BUFFER_SIZE)] #splite data into correct chunks
    data_list = []
    for data in splt_data:
        try:
            byte_data = data.encode('utf-8') # Convert the string to bytes
        except AttributeError:
            byte_data = data
            pass

        if len(byte_data) < BUFFER_SIZE: 
            byte_data = byte_data.ljust(BUFFER_SIZE, b'\x00') # Pad the byte array with spaces (0x20) or null bytes (0x00) if it is too short
        else:
            byte_data = byte_data[:BUFFER_SIZE] # Truncate the byte array if it is too long
        data_list.append(byte_data) #save all messages to list
    return data_list #return list

def send_sym_data(conn, key, data):
    if type(data) == type(""):
        data = data.encode()
    iv, encrypted_data = CryptoFunc.encrypt_data_sym(key, data)
    send_data(conn, iv)
    send_data(conn, encrypted_data)

def recv_sym_data(conn, key):
    iv = receive_data(conn)
    encrypted_data = receive_data(conn)
    return CryptoFunc.decrypt_data_sym(key, iv, encrypted_data)