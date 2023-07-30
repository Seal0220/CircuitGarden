import socket, json, re

def send_udp_message(location):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 1900))
    
    clinets = []
    with open('./ip.json', 'r') as ips:
        _Json = json.load(ips)
        Devices = _Json['Location'][location]['Devices']
        for device in Devices:
            clinets.append((device["IP"], device["Port"]))

    print(clinets)
    
    
    while True:
        if (msg := input()):
            for clinet in clinets:
                server_socket.sendto(f'[SERVER]{msg}'.encode(), clinet)
                
        message, addr = server_socket.recvfrom(1024)
        print(f"Received message: {message} from {addr}")


send_udp_message('CAT-Office')
