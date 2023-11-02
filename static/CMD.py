import GET, IO, SET
import machine
from ubinascii import a2b_base64


class CMDs:
    @staticmethod
    async def update(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] updating')
        await sendHost('updating')
        file_raw, name = args
        with open(name, 'wb') as file:
            file_raw_decode = a2b_base64(file_raw)
            file.write(file_raw_decode)
            
        await sendHost('updated')
    
    @staticmethod
    async def geton(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] geton')
        await sendHost(f'running [{await GET.getTime()} s]')
            
    @staticmethod
    async def breeze(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] breeze')
        await sendHost('breeze')
        await IO.breeze()
        
    @staticmethod
    async def breezeoff(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] breezeoff')
        await sendHost('breezeoff')
        await IO.breezeoff()
            
    @staticmethod
    async def beep(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] beep')
        await sendHost('beep')
        await IO.beep() 
            
    @staticmethod
    async def sound(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] sound')
        await sendHost('sound')
        await IO.sound() 
            
    @staticmethod
    async def intro(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] intro!!')
        await sendHost('intro start')
        await SET.setIsOnline(True)
        await SET.setIsLight(True)
        await IO.neopixelIn()
        await sendHost('intro finish')
        
    @staticmethod
    async def flashon(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] flash!!')
        await SET.setIsOnline(True)
        await sendHost('flash on')
        await IO.neopixelFlashOn(True)
        
    @staticmethod
    async def flashoff(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] flash!!')
        await sendHost('flash off')
        await IO.neopixelFlashOn(False)
        if await GET.getIsLight():
            await IO.neopixelLight()
        else:
            await IO.neopixelOn()
            
    @staticmethod
    async def lighton(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] light on!!')
        await sendHost('light on')
        await SET.setIsOnline(True)
        await SET.setIsLight(True)
        await IO.neopixelLight()
        
    @staticmethod
    async def lightoff(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] light off!!')
        await sendHost('light off')
        await SET.setIsLight(False)
        await IO.neopixelOn()
    
    @staticmethod
    async def on(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] on!!')
        await sendHost('on!!')
        await SET.setIsOnline(True)
        
        if await GET.getIsLight():
            await IO.neopixelLight()
        else:
            await IO.neopixelOn()
        
    @staticmethod
    async def setcolor(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] setcolor!!')
        
        rgb = []
        if args[0] in ('off', '_'):
            rgb = await GET.getOriginalColor()
            await SET.setIsSetColor(False)
            await SET.setColor(rgb)
        else:
            rgb = list(map(int, args[0].split(',')))
            await SET.setColor(rgb)
            await SET.setIsSetColor(True)
            
        await sendHost(f'setcolor {rgb}!!')
        await IO.neopixelLight()
        
    @staticmethod
    async def setid(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] setid!!')
        id = int(args[0])
        await sendHost(f'setid {id}!!')
        await SET.setColor(rgb)
        await IO.neopixelLight()
            
    @staticmethod
    async def off(args):
        from UDP import sendHost
        print(f'[{await GET.getTime()}][CMD] off!!')
        await sendHost('off!!')
        await SET.setIsOnline(False)
        await IO.neopixelFlashOn(False)
        await IO.neopixelOff()
        
    
    @staticmethod
    async def staticon(args):
        IO.isStatic = True
        
    @staticmethod
    async def staticoff(args):
        IO.isStatic = False
    

            
    @staticmethod
    async def reset(args):
        machine.reset()
                     

async def CMD(msg):
    try:      
        cmd, *args = msg.split()
        print(f'[{await GET.getTime()}][CMD] cmd: {cmd}, arg: {args}')
        
        await getattr(CMDs, cmd, None)(args)
        
    except Exception as e:
        print(f'[{await GET.getTime()}][CMD][CMD][Error] {e}')