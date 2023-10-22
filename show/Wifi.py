import GET, SET
import network
import uasyncio as asyncio
from ubinascii import hexlify
import utime as time
from collections import OrderedDict


wifi = None
name = 'WIFI'
SSID = ID = macAddress = IP = IPHead = group = ''
IDRange = hosts = []
port = 1900


# {terrible things below}-----------------------------------------------

async def __init__():
    global macAddress, wifi, ID, name
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    
    ID = await GET.getID()
    macAddress = await getMacAddress()
    
    print(f'[{name}] Initialized')


async def nearbyAP():
    print(f'\n[{await GET.getTime()}][{name}] Nearby AP: ')
    print(*await getNearbyAP(), sep='\n', end='\n\n')


async def connectWIFI():
    global wifi, name, SSID, macAddress, IP, ID, port, group, IDRange, IPHead, hosts, color
    
    SSID, *IPconfig, port = await GET.getIPconfig()
    IP = IPconfig[0]
    IPHead = await GET.getIPHead()
    password = await GET.getPassword()
    group, IDRange, color = await GET.getGroup(ID)
    await SET.setOriginalColor(color)
    hosts = await GET.getHostIP()
    
    wifi.connect(SSID, password)
    wifi.ifconfig(IPconfig)
    
    connecting_time = 0
    try:
        while (connecting_time := connecting_time+1) <= 30:
            wifistatus = {
                    network.STAT_CONNECTING: f'Connecting "{SSID}" ... ({connecting_time} s)',
                    network.STAT_IDLE: 'WIFI is idle.',
                    network.STAT_WRONG_PASSWORD: 'WIFI connection failed due to wrong password.',
                    network.STAT_NO_AP_FOUND: 'WIFI connection failed because no access point was found.',
                    network.STAT_GOT_IP: 'WIFI is connected and has an IP address.'
                    }
                        
            print(f'[{await GET.getTime()}][{name}][STATUS] {wifistatus.get(wifi.status(), "Unknown WIFI status.")}')
            
            if await isconnected():
                print()
                print(f'[{await GET.getTime()}][{name}][INFO] WIFI connected: {await isconnected()}')
                print(f'[{await GET.getTime()}][{name}][INFO] MAC address: {macAddress}')
                print(f'[{await GET.getTime()}][{name}][INFO] IP address: {IP} ', dict(zip(('IP', 'Subnet mask', 'Gateway', 'DNS'), wifi.ifconfig())))
                print()
                break
            
            await asyncio.sleep(1)
        else:
            print(f'[{await GET.getTime()}][{name}][ERROR] WIFI connection FAILED! TIMEOUT (Wrong password or Poor signal ...)')
                
    except Exception as e:
        print(f'[{await GET.getTime()}][{name}][ERROR] {type(e)} {e}')
        
    finally:
        return await isconnected()


async def isconnected():
    global wifi
    return wifi.isconnected()


async def getMacAddress():
    global wifi
    _macAdd = hexlify(wifi.config('mac')).decode()
    return ':'.join(_macAdd[i:i+2] for i in range(0, len(_macAdd), 2))
    
    
async def getNearbyAP():
    global wifi
    return map(lambda s: OrderedDict(zip(('ssid','bssid','channel','RSSI','security','hidden'),s)), wifi.scan())


# Initialize
asyncio.run(__init__())