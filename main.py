import uasyncio as asyncio
import json
import socket
import ubinascii
import network
import gc
from machine import Pin  #, freq
import utime as time
from collections import OrderedDict


button = Pin(17, Pin.IN, Pin.PULL_UP)
led = Pin(2, Pin.OUT)

class WIFI():
    def __init__(self):
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.name = self.__class__.__name__
        self.macAddress = ''
        self.IP = ''
        self.Broadcaster = None        
        print(f'[{self.name}] Nearby AP: ')
        print(*self.NearbyAP(), sep='\n', end='\n\n')
    
    def NearbyAP(self):
        return map(lambda s: OrderedDict(zip(('ssid','bssid','channel','RSSI','security','hidden'),s)), self.wifi.scan())
    
    async def ConnectWIFI(self, SSID, password):
        self.wifi.connect(SSID, password)
        connecting_time = 0
        def WIFIstatus(status):
            print(f'[{self.name}][STATUS] ', end='')
            if status == network.STAT_IDLE:
                print("WIFI is idle.")
            elif status == network.STAT_CONNECTING:
                print(f'Connecting "{SSID}" ... ({connecting_time} s)')
            elif status == network.STAT_WRONG_PASSWORD:
                print("WIFI connection failed due to wrong password.")
            elif status == network.STAT_NO_AP_FOUND:
                print("WIFI connection failed because no access point was found.")
            elif status == network.STAT_GOT_IP:
                print("WIFI is connected and has an IP address.")
            else:
                print("Unknown WIFI status.")
        
        try:
            while (connecting_time := connecting_time+1) <= 30:
                await asyncio.sleep(1)
                
                WIFIstatus(self.wifi.status())
                
                if self.wifi.isconnected():
                    self.macAddress = self.__MacAddress()
                    self.IP = self.__IP()
                    print()
                    print(f'[{self.name}][INFO] WIFI connected: {self.wifi.isconnected()}')
                    print(f'[{self.name}][INFO] MAC address: {self.macAddress}')
                    print(f'[{self.name}][INFO] IP address: {self.IP} ', dict(zip(('IP', 'Subnet mask', 'Gateway', 'DNS'), self.wifi.ifconfig())))
                    print()
                    self.Broadcaster = self.UDPBroadcaster(self.IP, SSID)
                    break
            else:
                print(f'[{self.name}][ERROR] WIFI connection FAILED! TIMEOUT (Wrong password or Poor signal ...)')
                    
        except Exception as e:
            print(f'[{self.name}][ERROR] {e} {e.__class__}')

    def __MacAddress(self):
        _macAdd = ubinascii.hexlify(self.wifi.config('mac')).decode()
        return ':'.join(_macAdd[i:i+2] for i in range(0, len(_macAdd), 2)
                        )

    def __IP(self):
        return self.wifi.ifconfig()[0]

    class UDPBroadcaster():
        def __init__(self, IP, SSID):
            self.IP = IP
            self.port = 1900
            self.SSID = SSID
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.IP, self.port))
            self.socket.setblocking(False)
            self.receivers = self.GetIPs()
            self.name = self.__class__.__name__
            print(f'[{self.name}] Initialized')
            asyncio.create_task(self.Listen())

        def GetIPs(self):
            with open('./ip.json', 'r') as Json:
                _Json = json.load(Json)
                Devices = _Json['SSID'][self.SSID]['Devices']
                ips = [(device["IP"], device["Port"]) for device in Devices]
                ips.remove((self.IP, self.port))
                return ips

        async def Listen(self):
            print(f'[{self.name}] Start Listening...')
            while True:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    print(f'\n[{self.name}][{addr[0]}:{addr[1]}] Received message: {data.decode("utf-8")}')
                    await self.__Light()
                except OSError as e:
                    if str(e) == "[Errno 11] EAGAIN":
                        await asyncio.sleep(0)
                    else:
                        print(f'[{self.name}]{e} ...')

        async def __Light(self):
            t_start = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), t_start) <= 100:
                led.value(1)
            led.value(0)

        async def Broadcast(self, message):
            print()
            for reciever in self.receivers:
                while True:
                    gc.collect()
                    try:
                        self.socket.sendto(
                            str(message).encode('utf-8'), reciever)
                        print(f'[{self.name}] Sent {reciever}')
                        break
                    except OSError as e:
                        print(f'[{self.name}]{e} ...')
                        await asyncio.sleep(0.1)


async def button_handler(wifi):
    isPressed = False
    while True:
        isPressed = not bool(button.value())
        await asyncio.sleep(0.01)

        if not button.value() and not isPressed:
            led.value(1)
            gc.collect()
            await wifi.Broadcaster.Broadcast('HI')
            await asyncio.sleep(1)
        else:
            led.value(0)


if __name__ == '__main__':
    # freq(240000000)

    wifi = WIFI()
    asyncio.run(wifi.ConnectWIFI('TNUA-AP', 'ccnet'))
    # asyncio.run(wifi.ConnectWIFI('SEAL', 'password'))
    asyncio.run(button_handler(wifi))

