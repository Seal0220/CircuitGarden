import NeoPixel, GET, UDP
import gc
from random import randint
from machine import UART, PWM, Pin
import uasyncio as asyncio

isBeeping = 0
isLighting = 0
isFlashing = False
isStatic = True
neopixel = NeoPixel.NeoPixel(18, 8)
motor = Pin(32, Pin.OUT)
motor.off()

# {terrible things below}-----------------------------------------------

async def neopixelAdd(i = 1):
    neopixel+i
    
async def neopixelSub(i = 1):
    neopixel-i

async def neopixelLight():
    await neopixel.setColor(await GET.getColor())

async def neopixelOn():
    await neopixel.setColor((255,255,255))
    
async def neopixelOff():
    await neopixel.setColor((0,0,0))

async def neopixelFlashOn(_isFlashing):
    global isFlashing
    isFlashing = _isFlashing
    
    if isFlashing:
        asyncio.create_task(neopixelFlash())

async def neopixelFlash():
    global isFlashing
    colors = [(0,0,255), (0,255,0), (255,0,0), (255,255,0)]
    
    _i = 0
    while isFlashing:
        if (i := randint(0, len(colors)-1)) == _i:
            continue
        
        _i = i
        await neopixel.setColor(colors[i])
        await asyncio.sleep(0.1)
    
    
async def neopixelIn():
    global isFlashing
    colors = [(0,0,255), (0,255,0), (255,0,0), (255,255,0)]
        
    isFlashing = True
    asyncio.create_task(neopixelFlash())
    await asyncio.sleep(10)
    isFlashing = False
    
    await neopixel.setColor(colors[0])
    await asyncio.sleep(10)
    await neopixel.setColor(colors[1])
    await asyncio.sleep(10)
    await neopixel.setColor(colors[2])
    await asyncio.sleep(10)
    await neopixel.setColor(colors[3])
    await asyncio.sleep(10)
    
    isFlashing = True
    asyncio.create_task(neopixelFlash())
    await asyncio.sleep(15)
    isFlashing = False
    
    await neopixelLight()


async def light():
    try:
        global isLighting
        
        led = Pin(2, Pin.OUT)
        isLighting +=1
        led.value(1)
        await asyncio.sleep(0.1)
        isLighting -=1
        if not isLighting:
            led.value(0)
        
    except Exception as e:
        print(f'[{await GET.getTime()}][IO][light][Error] {e}')


async def sound():
    _UART1 = UART(1, baudrate=9600, tx=17, rx=16)
    try:
        print(f'[{await GET.getTime()}][IO][sound] start writing...')
        
        query = bytes([0x7e, 0xFF, 0x06, 0x06, 0x00, 0x00, 15, 0xEF])
        _UART1.write(query)
        await asyncio.sleep_ms(500)
        query = bytes([0x7e, 0xFF, 0x06, 0x03, 0x00, 0x00, 1, 0xEF])
        _UART1.write(query)
        await asyncio.sleep_ms(10)
        print(f'[{await GET.getTime()}][IO][sound] end')
    
    except Exception as e:
        print(f'[{await GET.getTime()}][IO][sound][Error] {e}')


async def beep(time = 0.3):
    global isBeeping
    try:
        isBeeping +=1
        pwm = PWM(Pin(4))
        pwm.freq(2000)
        pwm.duty(512)
        await asyncio.sleep(time)
        isBeeping -=1
        if not isBeeping:
            pwm.deinit()
            
    except Exception as e:
        print(f'[{await GET.getTime()}][IO][beep][Error] {e}')
        
        
async def breeze(time = 5):
    global motor
    motor.on()
    await asyncio.sleep(time)
    motor.off()
    
    
async def breezeoff():
    global motor
    motor.off()
    
        
async def button():
    global neopixel
    
    _button = Pin(19, Pin.IN, Pin.PULL_UP)
    led = Pin(2, Pin.OUT)
    
    isPressed = False
    while True:
        # gc.collect()
        try:
            isPressed = not bool(_button.value())
            await asyncio.sleep_ms(10)
            
            if not _button.value() and not isPressed:
                led.value(1)
                asyncio.create_task(breeze())
                # asyncio.create_task(neopixelAdd())
                asyncio.create_task(UDP.broadcast('HI'))
                
                await asyncio.sleep(1)
                
            else:
                led.value(0)

        except Exception as e:
            print(f'[{await GET.getTime()}][IO][button][Error] {e}')
            
            
            
async def static():
    global isStatic, isFlashing
    await neopixelLight()
    print(f'[{await GET.getTime()}][IO][static] LIGHT ON')
    
    sec = 0
    try:
        while True:
            if isStatic:
                if sec == 0 and not isFlashing:
                    print(f'[{await GET.getTime()}][IO][static] ON')
                    asyncio.create_task(neopixelFlashOn(True))
                elif sec == 10 and isFlashing:
                    print(f'[{await GET.getTime()}][IO][static] OFF')
                    asyncio.create_task(neopixelFlashOn(False))
                    isFlashing = False
            
            sec += 1
            if sec >70:
                sec = 0
                
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f'[{await GET.getTime()}][IO][static] {e}')
            
