from neopixel import NeoPixel as NP
from machine import Pin
import uasyncio as asyncio
import GET

class NeoPixel(NP):
    def __init__(self, pin, num):
        super().__init__(Pin(pin, Pin.OUT), num)
        
        self.color = [0,0,0]
        if asyncio.run(GET.getIsOnline()):
            if asyncio.run(GET.getIsLight()):
                self.color = asyncio.run(GET.getColor())
            else:
                self.color = [255,255,255]

        super().fill(self.color)
        super().write()
        
        self._color = self.color
        self.light = 0

    def __add__(self, i):
        self.light = self.light+1 % 4
        asyncio.create_task(self.lighting())

    def __sub__(self, i):
        self.light = self.light-1 % 4
        asyncio.create_task(self.lighting())
        
    async def setColor(self, rgb, smooth = True, s = 0.25):           
        self.color = list(rgb)
        
        if smooth:
            _time = 0
            rate = 0.01
            _rgb = [int((self.color[i] - self._color[i])/s*rate) for i in range(3)]
            
            while _time <= s and self._color != self.color:
                for i in range(3):
                    self._color[i] += _rgb[i]
                
                super().fill(self._color)
                super().write()
                _time += rate
                await asyncio.sleep_ms(10)
            else:
                self._color = self.color
                
        super().fill(self.color)
        super().write()
            

    async def lighting(self):
        color = await self.setHSV(72*self.light)
        super().fill(color)
        super().write()

    async def setHSV(self, h: float, s: float = 1, v: float = 1):
        _h = h / 60.0
        i = int(_h) % 6
        f = _h - int(_h)
        p = v * (1 - s)
        q = v * (1 - f * s)
        r = v * (1 - (1 - f) * s)
        if i == 0:
            return (round(v * 255), round(r * 255), round(p * 255))
        elif i == 1:
            return (round(q * 255), round(v * 255), round(p * 255))
        elif i == 2:
            return (round(p * 255), round(v * 255), round(r * 255))
        elif i == 3:
            return (round(p * 255), round(q * 255), round(v * 255))
        elif i == 4:
            return (round(r * 255), round(p * 255), round(v * 255))
        elif i == 5:
            return (round(v * 255), round(p * 255), round(q * 255))
