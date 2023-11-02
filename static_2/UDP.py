import IO, GET, CMD
from Wifi import SSID, IP, port, macAddress, ID, group, IDRange, IPHead, hosts
import json, gc, machine
import socket as sk
import uasyncio as asyncio


socket = None
name = 'UDP'


# {terrible things below}-----------------------------------------------

async def __init__():
    global socket, name
    
    socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
    socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
    socket.bind((IP, port))
    socket.setblocking(False)
    
    print(f'[{name}] Initialized')


async def listen():   
    global socket, name
       
    await sendHost(f'[{IP}] online!!')
    
    print(f'[{await GET.getTime()}][{name}][Listen] Start Listening...')
    while True:
        try:
            data, addr = socket.recvfrom(1024*25)
            
            recvID, msg = data.decode("utf-8").split(',', 1)
            print(f'\n[{await GET.getTime()}][{name}][Listen][[{recvID}]{addr[0]}:{addr[1]}] Received message: {msg}')
            
            if recvID == '-1':
                asyncio.create_task(CMD.CMD(msg))
                
            asyncio.create_task(IO.light())
            
        except Exception as e:
            if str(e) == "[Errno 11] EAGAIN":
                await asyncio.sleep(0)
            else:
                print(f'[{await GET.getTime()}][{name}][Listen][ERROR] {e} ...') 
                machine.reset()
        
        
async def send(message, reciever):
    global socket, name
    
    while True:
        # gc.collect()
        try:
            msg = f"{ID},{message}"
            socket.sendto(msg.encode('utf-8'), reciever)
            print(f'[{await GET.getTime()}][{name}][Send] ( {msg} ) to {reciever}')
            break
        except Exception as e:
            print(f'[{await GET.getTime()}][{name}][Send][{reciever}]{e} ...')
            await asyncio.sleep(1)


async def sendHost(message):
    for host in hosts:
        await send(message, (host, port))


async def broadcast(message):
    global socket, name
    
    await send(message, (hosts[0], port))
    print(f'[{await GET.getTime()}][{name}][Broadcast] Broadcasting from ( {IPHead+str(IDRange[0])} to {IPHead+str(IDRange[1])} )')

        

# Initialize
asyncio.run(__init__())