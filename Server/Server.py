import tkinter as tk
# from tkinter import ttk
import socket, json, re, base64, ast, time
from datetime import datetime
from threading import Thread




def send(msg, ips=[(f'192.168.0.{i}',1900) for i in range(3,255)]):
    if len(ips) >=2:
        print(f'{datetime.now().strftime("%H:%M:%S")} Send message: {msg} to [{ips[0]} - {ips[-1]}]')
    else:
        print(f'{datetime.now().strftime("%H:%M:%S")} Send message: {msg} to [{ips}')
        
    for client in ips:
        try:
            server_socket.sendto(f'-1,{msg}'.encode('utf-8'), client)
            
        except Exception as e:
            if  not re.search(r'Errno 64|Errno 65', str(e)):
                print(f'{datetime.now().strftime("%H:%M:%S")} {e} {client}')
                
def recv():
    while True:
        message, addr = server_socket.recvfrom(1024*50)
        message_decode = message.decode()
        print(f'{datetime.now().strftime("%H:%M:%S")} Received message: {message_decode} from {addr}')



with open('IPs.json', 'r') as IPs:
    groups = dict(zip(('A','B','C','D','E'), [{'range' : ids['ID'],'controller' : ids['controller'], 'color': ids['Color']} for ids in json.loads(IPs.read())['Groups'].values()]))
    print(groups)

class CMDs:
    @staticmethod
    def getGroupIPs(group):
        if group == '_':
            return [(f'192.168.0.{i}',1900) for i in range(3,255)]
        else:
            return [(f'192.168.0.{i}',1900) for i in range(*groups.get(group)['range'])]
    
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
    def intro(group='_'):
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
    def __init__(self, root, group, row, col=0, methods = ['on','intro','flashon','flashoff','lighton','lightoff','breeze','sound','reset','setcolor','off']):
        def rgb_to_hex(r, g, b):
            return '#{:02x}{:02x}{:02x}'.format(r, g, b)
        
        
        self.color = rgb_to_hex(*groups.get(group, {'color':[0,0,0]})['color'])
        self.id = {}
        
        
        frame_btns = tk.Frame(root)
        frame_btns.grid(row=row)
        tk.Label(frame_btns, text=group).grid(row=row, column=col, padx=5, pady=5)
        for i, mth in enumerate(methods):
            tk.Button(frame_btns, text=mth, command=lambda mth=mth: getattr(CMDs, mth)(group), width=4, height=3, highlightbackground=self.color).grid(row=row, column=col+1+i, padx=5, pady=5)
        
        
        frame_ids = tk.Frame(root)
        frame_ids.grid(row=row+1, column=col)
        
        if (controller := groups.get(group, {'controller': None})['controller']):
            tk.Label(frame_ids, text=controller, bg='black', fg='white', width=2, height=1).grid(row=row, column=0, padx=20, pady=5)
        for i, id in enumerate(range(*groups.get(group, {'range':[0]})['range'])):
            self.id[str(id)] = tk.Label(frame_ids, text=id, bg='black', fg='white', width=2, height=1).grid(row=row, column=1+i, padx=5, pady=5)
            
        tk.Label(frame_ids, width=2, height=1).grid(row=row+1, column=0, padx=5, pady=5)

    def setStatus(self, key, value):
        try:
            # self.id[key] = value
            pass
        except Exception as e:
            print(e)

def main():
    root = tk.Tk()
    root.title('Commands Interface')
    # root.geometry('1000x1000')

    A = GroupBtn(root, 'A', 1)
    B = GroupBtn(root, 'B', 3)
    C = GroupBtn(root, 'C', 5)
    D = GroupBtn(root, 'D', 7)
    All = GroupBtn(root, '_', 9, methods = ['on','intro','flashon','flashoff','lighton','lightoff','breeze','sound','reset','setcolor','off', 'geton'])

    root.mainloop()

if __name__ == '__main__':
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('192.168.0.3', 1900))
    
    recv_thread = Thread(target=recv)
    recv_thread.start()
    
    main()

    
