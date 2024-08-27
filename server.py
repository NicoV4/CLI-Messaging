import socket
import threading
import Server.Main
import CryptoFunc
import os

if __name__ == "__main__":
    bind_addr = "0.0.0.0"
    bind_port = 7544
    private_key, public_key_pem = CryptoFunc.gen_keys_asym() #generate rsa key pair
    sym_key = os.urandom(32)
    rooms_list = []
    create_room_allow = True
    
    print(public_key_pem)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind((bind_addr, bind_port))
    soc.listen(9999)
    print(f"listening...\naddr: {bind_addr}\nport: {bind_port}")
    while True:
        client, addr = soc.accept()
        threading.Thread(target=Server.Main.listener, args=(client, addr, private_key, public_key_pem, rooms_list, create_room_allow, sym_key)).start()