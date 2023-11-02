import socket, json, re, base64, ast, time
from datetime import datetime
from threading import Thread

def send_udp_message(location):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('192.168.0.2', 1900))
    # server_socket.setblocking(False)

    # clients = []
    # with open('./ip.json', 'r') as ips:
    #     _Json = json.load(ips)
    #     Devices = _Json['Location'][location]['Devices']
    #     for device in Devices:
    #         clients.append((device["IP"], device["Port"]))

    # print(clients)

    def recv():
        with open('IPs.json', 'r') as IPs:
            groups = dict(zip(('A','B','C','D','E'), [ids['ID'] for ids in json.loads(IPs.read())['Groups'].values()]))
            
        while True:
            message, addr = server_socket.recvfrom(1024*50)
            message_decode = message.decode()
            print(f'{datetime.now().strftime("%H:%M:%S")} Received message: {message_decode} from {addr}')
            
            if not re.search(r'running|off!!|on!!|online!!', message_decode):
                ID = int(addr[0].split('.')[-1])

                for key, ids in groups.items():
                    if ids[0] <= ID <= ids[1]:
                        _send(message, ips=[(f'192.168.0.{i}',1900) for i in range(ids[0], ids[1]+1) if i != ID])
                
            
    def _send(msg, ips=[(f'192.168.0.{i}',1900) for i in range(3,255)]):
        print(f'{datetime.now().strftime("%H:%M:%S")} Send message: {msg} to [{ips[0]} - {ips[-1]}]')
        for client in ips:
            try:
                server_socket.sendto(f'-1,{msg}'.encode('utf-8'), client)
             
            except Exception as e:
                if  not re.search(r'Errno 64|Errno 65', str(e)):
                    print(f'{datetime.now().strftime("%H:%M:%S")} {e} {client}')

    def send():
        def IP(text):
            try:
                pattern_ip = r"-a\s+\[(.*?)\]"
                matches = map(lambda ip: (ip.strip(),1900),re.search(pattern_ip, text).group(1).split(','))
                text = re.sub(pattern_ip, '', text)
                return [text, matches]
            except:
                return [text, [(f'192.168.0.{i}',1900) for i in range(3,256)]]
        
                    
        while True:
            if (msg := input()):
                if msg.startswith('update'):
                    text, ips = IP(msg)
                    cmd, *args = text.split()
                    print(f'cmd: {cmd}, arg: {args}')
                    args_iter = iter(args)
                    
                    # print(ips)

                    if cmd == 'update':
                        try:
                            
                            path = next(args_iter)
                            with open(path, 'rb') as file:
                                file_raw = base64.b64encode(file.read()).decode()

                            name = next(args_iter)
                            if ips:
                                _send(msg=f'{cmd} {file_raw} {name}', ips=ips)
                            else:
                                _send(f'{cmd} {file_raw} {name}')
                                
                            # print(f'ips: {ips}, path: {path}, name: {name}')
                        except Exception as e:
                            print(e)
                    
                    
                    
                else:
                    _send(msg)
                    
    def sendLoop():
        while True:
            _send('breeze')
            time.sleep(30)



    send_thread = Thread(target=send)
    recv_thread = Thread(target=recv)
    #sendLoop_thread = Thread(target=sendLoop)

    send_thread.start()
    recv_thread.start()
    #sendLoop_thread.start()

    send_thread.join()
    recv_thread.join()
    #sendLoop_thread.join()

if __name__ == '__main__':
    send_udp_message('SEAL')
