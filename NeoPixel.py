class NeoPixel(neopixel.NeoPixel):
    def __init__(self, pin, num):
        super().__init__(Pin(pin, Pin.OUT), num)
        super().fill((255, 255, 255))
        super().write()

    def __add__(self, i):
        self[i] = (0, 0, 255)
        super().write()

    def __sub__(self, i):
        self[i] = (255, 255, 255)
        super().write()
        
        

class Neo2(neopixel.NeoPixel):
    def __init__(self, pin, num):
        super().__init__(Pin(pin, Pin.OUT), num)
        super().fill((255, 255, 255))
        super().write()
        
    def setHSV(self, h: float, s: float, v: float):
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
            
    def Loop(self):
        color = 0
        while True:
            print(color)
            for i in range(8):
                self[i] = self.setHSV(color,1,1)
            super().write()
            color+=0.1
            
            if color>=360:
                color=0
                
            # time.sleep_ms(100)
            
    def Round(self):
        color = i = 0
        while True:
            print(color)
            self[i] = self.setHSV(color+i,1,1)
            super().write()
            
            color+=8.1
            i+=1
            
            if color>=360:
                color=0
                
            if i>=8:
                i=0
                
            
            time.sleep_ms(100)
            