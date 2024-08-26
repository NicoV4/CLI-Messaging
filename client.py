import sys
import socket
import base64
from Client.DnsFunc import dns_lookup
from Client.ConnFunc import *
from CryptoFunc import *
from Client.TerminalFunc import *

if __name__ == "__main__":
    domain_name = "domain.com"
    ip_address = dns_lookup(domain_name)
    ip_address = "localhost"
    
    private_key, public_key_pem = gen_keys() #generate rsa key pair
    print(public_key_pem)
    
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.connect((ip_address, 7544))
    
    server_pub = serialize_pub(crypto_key_exchange(soc, public_key_pem)) #receive server public key + serialize key
    print(server_pub)
    
    t_color = terminal_color() #choose terminal color
    print(t_color + "changed terminal color...")
    
    username = select_username(soc, private_key, server_pub) #let user select username
    
    while True:
        command = input(f"{username}> ") #get command from user
        #print(f"command: {command}")
        if not command:
            continue
        elif command == "exit":
            sys.exit()
        else:
            Client.ConnFunc.send_data(soc, CryptoFunc.encrypt_data(server_pub, command)) #send command to server
            server_result = CryptoFunc.decrypt_data(private_key, Client.ConnFunc.receive_data(soc)).decode() #receive result from server
            if "Connected to room" in server_result: #if connected to a room
                chat(soc, private_key, server_pub) #run chat func
            else:
                print(server_result)
