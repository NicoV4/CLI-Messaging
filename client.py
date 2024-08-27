import sys
import socket
import base64
from Client.DnsFunc import dns_lookup
from ConnFunc import *
from CryptoFunc import *
from Client.TerminalFunc import *

if __name__ == "__main__":
    domain_name = "domain.com"
    ip_address = dns_lookup(domain_name)
    ip_address = "localhost"
    port = 7544
    
    private_key, public_key_pem = gen_keys_asym() #generate rsa key pair
    print(public_key_pem)
    
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((ip_address, port))
    print(f"connect to server... {ip_address}:{port}")
    
    encoded_pub = base64.b64encode(public_key_pem) #base64 encode pub key
    send_data(soc, encoded_pub)
    server_pub = base64.b64decode(receive_data(soc))
    print(server_pub)
    server_pub = serialize_pub(server_pub) #receive server public key + serialize key
    print(server_pub)
    
    t_color = terminal_color() #choose terminal color
    print(t_color + "changed terminal color...")
    
    username = select_username(soc, private_key, server_pub) #let user select username
    
    sym_key = base64.b64decode(CryptoFunc.decrypt_data_asym(private_key, ConnFunc.receive_data(soc))) #receive symmetric key
    
    while True:
        command = input(f"{username}> ") #get command from user
        #print(f"command: {command}")
        if not command:
            continue
        elif command == "exit":
            sys.exit()
        else:
            ConnFunc.send_sym_data(soc, sym_key, command) #send command to server
            server_result = ConnFunc.recv_sym_data(soc, sym_key).decode() #receive result from server
            if "Connected to room" in server_result: #if connected to a room
                chat(soc, username, sym_key) #run chat func
            else:
                print(server_result)
