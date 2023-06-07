import json
import _thread
import socket
import ubinascii
import network
import gc
from machine import Pin, freq
import utime as time



class WIFI():
    def __init__(self):
        self.wifi = network.WLAN(network.STA_IF)
        self.wifi.active(True)
        self.name = self.__class__.__name__
        self.macAddress = ''
        self.IP = ''
        self.Broadcaster = None
        
        print(*self.wifi.scan(), sep='\n')

    def ConnectWIFI(self, SSID, password):
        self.wifi.connect(SSID, password)
        connecting_time = 0
        try:
            while not (self.wifi.isconnected() or (connecting_time := connecting_time+1) > 10):
                time.sleep_ms(1000)
                print(f'[{self.name}] Connecting "{SSID}" ... ({connecting_time} s)')
            else:
                print(f'[{self.name}] WIFI connected:', self.wifi.isconnected())
                self.macAddress = self.__MacAddress()
                self.IP = self.__IP()
                print(f'[{self.name}] MAC address:', self.macAddress)
                print(f'[{self.name}] IP address:', self.IP)
                self.Broadcaster = self.UDPBroadcaster(self.IP)
        except Exception as e:
            print(e)

    def __MacAddress(self):
        _macAdd = ubinascii.hexlify(self.wifi.config('mac')).decode()
        return ':'.join(_macAdd[i:i+2] for i in range(0, len(_macAdd), 2))

    def __IP(self):
        return self.wifi.ifconfig()[0]

    class UDPBroadcaster():
        def __init__(self, IP):
            self.IP = IP
            self.port = 1900
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.IP, self.port))
            self.receivers = self.GetIPs()
            self.name = self.__class__.__name__
            
        def GetIPs(self):
            with open('./ip.json', 'r') as Json:
                _Json = json.load(Json)
                Devices = _Json['SSID']['TNUA-AP-N']['Devices']
                ips = [(device["IP"], device["Port"]) for device in Devices]
                ips.remove((self.IP, self.port))
                return ips

        def Listen(self):
            while True:
                try:
                    data, addr = self.socket.recvfrom(1024)
                    print(f'\n[{self.name}][{addr[0]}:{addr[1]}] Received message: {data.decode("utf-8")}')
                    self.__Light()
                except OSError as e:
                    print(f'[{self.name}]{e} ...')
        
        def __Light(self):
            t_start = time.ticks_ms()
            while time.ticks_diff(time.ticks_ms(), t_start) <= 100:
                led.value(1)
            led.value(0)

        def Broadcast(self, message):
            print()
            for reciever in self.receivers:
                while True:
                    gc.collect()
                    try:
                        self.socket.sendto(str(message).encode('utf-8'), reciever)
                        print(f'[{self.name}] Sent {reciever}')
                        break
                    except OSError as e:
                        print(f'[{self.name}]{e} ...')
                        time.sleep_ms(100)

        def Start(self):
            print(f'[{self.name}][{self.IP}:{self.port}] Start Listening thread')
            _thread.start_new_thread(self.Listen, ())

if __name__ == '__main__':
    freq(240000000)

    wifi = WIFI()
    wifi.ConnectWIFI('TNUA-DORM', '')
    wifi.Broadcaster.Start()

    button = Pin(17, Pin.IN, Pin.PULL_UP)
    led = Pin(2, Pin.OUT)
    isPressed = False

    while True:
        isPressed = not bool(button.value())
        time.sleep_ms(10)

        if not button.value() and not isPressed:
            led.value(1)
            gc.collect()
            wifi.Broadcaster.Broadcast('HI')
            time.sleep_ms(1000)
        else:
            led.value(0)