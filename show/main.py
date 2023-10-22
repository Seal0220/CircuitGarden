import UDP, IO
import uasyncio as asyncio


if __name__ == '__main__':
    print('[MAIN] start')

    asyncio.create_task(UDP.listen())
    asyncio.run(IO.button())
    
        
        