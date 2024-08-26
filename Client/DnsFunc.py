import socket

def dns_lookup(domain_name):
    try:
        ip_address = socket.gethostbyname(domain_name)
        return ip_address
    except socket.error as e:
        print(f"DNS lookup failed for {domain_name}: {e}")