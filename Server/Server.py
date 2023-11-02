import tkinter as tk
# from tkinter import ttk
import socket, json, re, base64, ast, time
from datetime import datetime
from threading import Thread
import logging


onlines = _onlines = recvs = set()
isFlashwhite = False
A = B = C = D = E = object

logging.basicConfig(filename='./Server/log-2023.10.29.log', level=logging.DEBUG, format='[%(asctime)s][%(levelname)s] %(message)s')

extends = {
    'A':[108,109,121,122,124,129],
    'B':[119,120,125],
    'C':[117,118,126,128,130],
    'D':[115,116,127],
}

with open('IPs.json', 'r') as IPs:
    groups = dict(zip(('A','B','C','D','E'), [{'range' : IDs['ID'],'controller' : IDs['controller'], 'color': IDs['Color']} for IDs in json.loads(IPs.read())['Groups'].values()]))
    print(groups)
    logging.debug(groups)


def send(msg, ips):
    if len(ips) >=2:
        pt = f'[SEND] {msg} to {[int(i[0].split(".")[-1]) for i in ips]}'
        print(f'[{datetime.now().strftime("%H:%M:%S")}] {pt}')
        logging.info(pt)
    else:
        pt = f'[SEND] {msg} to [{ips}]'
        print(f'[{datetime.now().strftime("%H:%M:%S")}] {pt}')
        logging.info(pt)
        
    for client in ips:
        try:
            server_socket.sendto(f'-1,{msg}'.encode('utf-8'), client)
            
        except Exception as e:
            if  not re.search(r'Errno 64|Errno 65', str(e)):
                pt = f'{e} {client}'
                print(f'[{datetime.now().strftime("%H:%M:%S")}] {pt}')
                logging.error(pt)
                
                
def setStatus(st, status):
    for ID in st:
        match CMDs.getIDGroup(ID):
            case 'A':
                A.setStatus(ID, status)
            case 'B':
                B.setStatus(ID, status)
            case 'C':
                C.setStatus(ID, status)
            case 'D':
                D.setStatus(ID, status)
            # case 'E':
            #     E.setStatus(ID, status)

def getOnline():
    global onlines, _onlines, recvs
    while True:
        try:
            pt = f'GETTING online...'
            print(f'[{datetime.now().strftime("%H:%M:%S")}] {pt}')
            logging.critical(pt)
            
            CMDs.geton()
            CMDs.geton('E')
            
            
            if _onlines:
                setStatus(onlines & _onlines, 'running')
                
                offlines = _onlines.difference(onlines) 
                setStatus(offlines, 'out')
                setStatus(recvs, 'recv')
                
                if offlines:
                    pt = f'OFFLINE: [{offlines}]'
                    print(pt)
                    logging.critical(pt)
            else:
                setStatus(onlines, 'online')
                
            _onlines = onlines
            onlines = set()
            recvs = set()

            time.sleep(5)
        except Exception as e:
            pt = f'{e}'
            print(f'[{datetime.now().strftime("%H:%M:%S")}] {pt}')
            logging.error(pt)

def sendCMD(msg):
    def IP(text):
        try:
            pattern_ip = r"\[(.*?)\]"
            matches = list(map(lambda ip: (f'192.168.0.{ip.strip()}',1900),re.search(pattern_ip, text).group(1).split(',')))
            text = re.sub(pattern_ip, '', text)
            return [text, matches]
        except:
            return [text, CMDs.getGroupIPs()]
    
    try:
        if msg:
            msg = str(msg)
            text, ips = IP(msg)
            if msg.startswith('update'):
                cmd, *args = text.split()
                pt = f'cmd: {cmd}, arg: {args}'
                print(f'[{datetime.now().strftime("%H:%M:%S")}] {pt}')
                logging.critical(pt)
                args_iter = iter(args)

                if cmd == 'update':
                    try:               
                        path = next(args_iter)
                        name = next(args_iter)
                        with open(path, 'rb') as file:
                            file_raw = base64.b64encode(file.read()).decode()
                        
                        if ips:
                            send(msg=f'{cmd} {file_raw} {name}', ips=ips)
                        else:
                            send(f'{cmd} {file_raw} {name}')

                    except Exception as e:
                        print(f'[{datetime.now().strftime("%H:%M:%S")}] {e}')
                        logging.error(e)
            else:
                send(msg, ips=ips)
    except:
        pass
        
                    
def recv():
    global onlines, _onlines
    while True:
        message, addr = server_socket.recvfrom(1024*50)
        message_decode = message.decode()
        pt = f'[RECV] {message_decode} from {addr}'
        print(f'[{datetime.now().strftime("%H:%M:%S")}] {pt}')
        logging.info(pt)
        
        ID, status = message_decode.split(',')
        if re.search(r'running', status):
            onlines.add(ID)
        elif re.search(r'online', status):
            setStatus([ID], 'online')
        else:
            recvs.add(ID)
            setStatus([ID], 'recv')
            # ID, status = message_decode.split(',')


class CMDs:
    @staticmethod
    def getIDGroup(ID):
        for group, content in groups.items():
            rng = content['range']
            extend = extends.get(group, [])
            
            if rng[0] <= int(ID) <= rng[1] or int(ID) in extend:
                return group
        
    @staticmethod
    def getGroupIDs(group = '_'):
        if group == '_':
            rng = [i for i in range(4,131)]
            for i, ext in extends.items():
                rng.extend(ext)
            return rng
        else:
            rng =  groups.get(group)['range']
            ips = [i for i in range(rng[0], rng[1]+1)]
            ips.extend(extends.get(group, []))

            return ips
        
    @staticmethod
    def getGroupIPs(group = '_'):
        return [(f'192.168.0.{i}',1900) for i in CMDs.getGroupIDs(group)]
    
    @staticmethod
    def update(group='_', args=None):            
        send('update', CMDs.getGroupIPs(group))

    
    @staticmethod
    def geton(group='_'):
        send('geton', CMDs.getGroupIPs(group))

            
    @staticmethod
    def breeze(group='_'):
        send('breeze', CMDs.getGroupIPs(group))
        
    @staticmethod
    def flow(group='_'):
        send('flow', CMDs.getGroupIPs(group))

    @staticmethod
    def breezeoff(group='_'):
        send('breezeoff', CMDs.getGroupIPs(group))

            
    @staticmethod
    def beep(group='_'):
        send('beep', CMDs.getGroupIPs(group))

            
    @staticmethod
    def sound(group='_'):
        send('sound', CMDs.getGroupIPs(group))

            
    @staticmethod
    def flash(group='_'):
        send('flash', CMDs.getGroupIPs(group))

            
    @staticmethod
    def lighton(group='_'):
        send('lighton', CMDs.getGroupIPs(group))

        
    @staticmethod
    def lightoff(group='_'):
        send('lightoff', CMDs.getGroupIPs(group))
        
    
    @staticmethod
    def flashon(group='_'):
        send('flashon', CMDs.getGroupIPs(group))
        
        
    @staticmethod
    def flashoff(group='_'):
        send('flashoff', CMDs.getGroupIPs(group))
        
    
    @staticmethod
    def flashwhiteon(group='_'):
        global isFlashwhite
        isFlashwhite = True
        def fw():
            global isFlashwhite
            send('lightoff', CMDs.getGroupIPs(group))
            while isFlashwhite:
                send('on', CMDs.getGroupIPs(group))
                time.sleep(1)
                send('off', CMDs.getGroupIPs(group))
                time.sleep(1)
                
            send('on', CMDs.getGroupIPs(group))
        
        fw_thread = Thread(target=fw)
        fw_thread.start()
        
        
    @staticmethod
    def flashwhiteoff(group='_'):
        global isFlashwhite
        isFlashwhite = False
        
    
    @staticmethod
    def intro(group='_'):
        CMDs.flashwhiteoff()
        send('intro', CMDs.getGroupIPs(group))
        

    @staticmethod
    def setcolor(group='_'):
        send('setcolor', CMDs.getGroupIPs(group))

        
    @staticmethod
    def setid(group='_'):
        send('setid', CMDs.getGroupIPs(group))
        
        
    @staticmethod
    def on(group='_'):
        send('on', CMDs.getGroupIPs(group))

            
    @staticmethod
    def off(group='_'):
        send('off', CMDs.getGroupIPs(group))


    @staticmethod
    def reset(group='_'):
        send('reset', CMDs.getGroupIPs(group))
        

class GroupBtn:
    def __init__(self, root, group, row, col=0, methods = ['on','intro','flashwhiteon','flashwhiteoff','flashon','flashoff','lighton','lightoff','breeze','sound','reset','off', 'geton']):
        def rgb_to_hex(r, g, b):
            return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        
        self.color = rgb_to_hex(*groups.get(group, {'color':[0,0,0]})['color'])
        self.IDs = {}
        
        
        frame_btns = tk.Frame(root)
        frame_btns.grid(row=row)
        tk.Label(frame_btns, text=group).grid(row=row, column=col, padx=5, pady=5)
        for i, mth in enumerate(methods):
            tk.Button(frame_btns, text=mth, command=lambda mth=mth: getattr(CMDs, mth)(group), width=4, height=3, highlightbackground=self.color).grid(row=row, column=col+1+i, padx=5, pady=5)
        
        
        frame_IDs = tk.Frame(root)
        frame_IDs.grid(row=row+1, column=col)
        
        if (controller := groups.get(group, {'controller': None})['controller']):
            tk.Label(frame_IDs, text=controller, bg='black', fg='white', width=2, height=1).grid(row=row, column=0, padx=20, pady=5)
        
        if group != '_':
            for i, ID in enumerate(CMDs.getGroupIDs(group)):
                label = tk.Label(frame_IDs, text=ID, bg='black', fg='white', width=2, height=1)
                label.grid(row=row+i//30, column=1+(i%30), padx=5, pady=5)
                self.IDs[str(ID)] = label
            
        tk.Label(frame_IDs, width=2, height=1).grid(row=row+1, column=0, padx=5, pady=5)

    def setStatus(self, ID, value):
        statusColor = {
            'off' : 'black',
            'running' : 'green',
            'online' : 'orange',
            'recv' : 'blue',
            'out' : 'red'
        }
        
        try:
            self.IDs[ID].config(bg=statusColor[value])
        except Exception as e:
            print(e)

def main():
    global A, B, C, D, E
    root = tk.Tk()
    root.title('Commands Interface')

    A = GroupBtn(root, 'A', 1)
    B = GroupBtn(root, 'B', 3)
    C = GroupBtn(root, 'C', 5)
    D = GroupBtn(root, 'D', 7)
    # E = GroupBtn(root, 'E', 9, methods=['on','flashon','flashoff','lighton','lightoff','flow','reset','off','geton'])
    All = GroupBtn(root, '_', 11)
    
    cmd_entry = tk.Entry(root)
    cmd_entry.grid(row=12, column=0, padx=5, pady=5)
    cmd_entry.bind('<Return>', lambda event, cmd_entry=cmd_entry: sendCMD(cmd_entry.get()))

    root.mainloop()

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('192.168.0.3', 1900))
    
    recv_thread = Thread(target=recv)
    getOnline_thread = Thread(target=getOnline)
    
    recv_thread.start()
    getOnline_thread.start()
    
    main()

    
