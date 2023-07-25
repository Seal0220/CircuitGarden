import uasyncio as asyncio
import json, socket, ubinascii, network, gc, neopixel
from machine import Pin, PWM, UART, ADC  #, freq
import utime as time
from collections import OrderedDict



button = Pin(17, Pin.IN, Pin.PULL_UP)
led = Pin(2, Pin.OUT)
led2 = Pin(19, Pin.OUT)
time_offset = time.time()


class NeoPixel(neopixel.NeoPixel):
    def __init__(self, pin, num):
        super().__init__(pin, num)
        super().fill((255, 255, 255))
        self.write()

    def __add__(self, i):
        self[i] = (0, 0, 255)

    def __sub__(self, i):
        self[i] = (255, 255, 255)


    
    
class WIFI:
    def __init__(self):
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.name = self.__class__.__name__
        self.macAddress = ''
        self.IP = ''
        self.Broadcaster = None        
        # print(f'[{self.name}] Nearby AP: ')
        # print(*self.NearbyAP(), sep='\n', end='\n\n')
        self._NearbyAP()
        # asyncio.create_task(self.GetRSSI())
        
    async def GetRSSI(self):
        while True:
            locater1_SSID, locater2_SSID = b'Xuan', b'SEAL'
            locater1_RSSI = locater2_RSSI = None
            
            APs = self.wifi.scan()
            for ap in APs:
                if ap[0] == locater1_SSID:
                    locater1_RSSI = ap[3]
                elif ap[0] == locater2_SSID:
                    locater2_RSSI = ap[3]
                if locater1_RSSI and locater2_RSSI:
                    break
                    
            print(f'{locater1_SSID.decode()}: {locater1_RSSI}, {locater2_SSID.decode()}: {locater2_RSSI}')
            
            # await asyncio.sleep(0.1)
        
    def _NearbyAP(self):
        print()
        print(f'[{self.name}] Nearby AP: ')
        print(*self.NearbyAP(), sep='\n', end='\n\n')
        # print(self.wifi.scan(), type(self.wifi.scan()))
        print()
        # await asyncio.sleep(0.1)
    
    def NearbyAP(self):
        return map(lambda s: OrderedDict(zip(('ssid','bssid','channel','RSSI','security','hidden'),s)), self.wifi.scan())
    
    def ConnectWIFI(self, location):
        with open('./ip.json', 'r') as Json:
            _json = json.load(Json)
            SSID = _json['Location'][location]['SSID']
            password = _json['Location'][location]['Password']
                
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
                time.sleep(1)
                
                WIFIstatus(self.wifi.status())
                
                if self.wifi.isconnected():
                    self.macAddress = self.__MacAddress()
                    self.IP = self.__IP()
                    print()
                    print(f'[{self.name}][INFO] WIFI connected: {self.wifi.isconnected()}')
                    print(f'[{self.name}][INFO] MAC address: {self.macAddress}')
                    print(f'[{self.name}][INFO] IP address: {self.IP} ', dict(zip(('IP', 'Subnet mask', 'Gateway', 'DNS'), self.wifi.ifconfig())))
                    print()
                    self.Broadcaster = self.UDPBroadcaster(self.IP, SSID, self.macAddress, location)
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
        def __init__(self, IP, SSID, macAddress, location):
            self.IP = IP
            self.port = 1900
            self.SSID = SSID
            self.macAddress = macAddress
            self.id = None
            self.location = location
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.IP, self.port))
            self.socket.setblocking(False)
            self.receivers = self.GetIPs()
            self.name = self.__class__.__name__
            self.isLighting = 0
            self.isBeeping = 0
            self.NeoPixel = NeoPixel(18, 8)
            
            # self.recvmsg = ''
            print(f'[{self.name}] Initialized')
            asyncio.create_task(self.Listen())

        def GetIPs(self):
            with open('./ip.json', 'r') as Json:
                _Json = json.load(Json)
                Devices = _Json['Location'][self.location]['Devices']
                ips = []
                for device in Devices:
                    if device['Mac Address'] == self.macAddress:
                        self.id = device['id']
                    else:
                        ips.append((device["IP"], device["Port"]))
                return ips

        async def Listen(self):
            print(f'[{self.name}][Listen] Start Listening...')
            while True:
                gc.collect()
                try:
                    data, addr = self.socket.recvfrom(1024)
                    id, msg = data
                    print(f'\n[{self.name}][Listen][[{id}]{addr[0]}:{addr[1]}] Received message: {msg.decode("utf-8")}')
                    asyncio.create_task(self.__Light())
                    asyncio.create_task(self.__Beep())
                    asyncio.create_task(self.__NeoPixel(id))
                    # asyncio.create_task(self.__soundUART())
                except Exception as e:
                    if str(e) == "[Errno 11] EAGAIN":
                        await asyncio.sleep(0)
                    else:
                        print(f'[{self.name}][Listen]{e} ...')

        async def __Light(self):
            self.isLighting +=1
            led.value(1)
            await asyncio.sleep(0.1)
            self.isLighting -=1
            if not self.isLighting:
                led.value(0)
        
        # async def __soundUART(self):
        #     soundUART = UART(1, baudrate=9600, tx=1, rx=3)
        #     soundUART.write(b'\x7E\xFF\x06\x03\x00\x00\x01\xFE\xF7\xEF')
        #     await asyncio.sleep(0.5)
        
        async def __Beep(self):
            self.isBeeping +=1
            pwm = PWM(Pin(4))
            pwm.freq(2000)
            pwm.duty(512)
            await asyncio.sleep(0.3)
            self.isBeeping -=1
            if not self.isBeeping:
                pwm.deinit()
                
        async def __NeoPixel(self, i):
            self.NeoPixel+=i
            self.NeoPixel.write()
            await asyncio.sleep_ms(500)
            self.NeoPixel-=i
            self.NeoPixel.write()
            

        async def Broadcast(self, message):
            async def _Send(message, reciever):
                while True:
                    gc.collect()
                    try:
                        self.socket.sendto((self.id, str(message).encode('utf-8')), reciever)
                        print(f'[{time.time()-time_offset}][{self.name}][Broadcast] Sent ( {message} ) to {reciever}')
                        break
                    except Exception as e:
                        print(f'[{time.time()-time_offset}][{self.name}][Broadcast][{reciever}]{e} ...')
                        await asyncio.sleep(1)
            
            for reciever in self.receivers:
                gc.collect()
                asyncio.create_task(_Send(message, reciever))


async def button_handler(wifi):
    isPressed = False
    while True:
        isPressed = not bool(button.value())
        await asyncio.sleep(0.01)

        if not button.value() and not isPressed:
            led.value(1)
            led2.value(1)
            gc.collect()
            await wifi.Broadcaster.Broadcast('HI')
            await asyncio.sleep(1)
        else:
            led.value(0)
            led2.value(0)

if __name__ == '__main__':
    
    wifi = WIFI()
    wifi.ConnectWIFI('Home')
    # wifi.ConnectWIFI('CAT-Office')
    asyncio.run(button_handler(wifi))
        
    

