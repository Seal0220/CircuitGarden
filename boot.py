import SEAL
print('[BOOT] \'SEAL\' imported')

import setup
print('[BOOT] \'setup\' imported')

import SET
print('[BOOT] \'SET\' imported')

SET.setTimeOffset()
print('[BOOT] Time Offset set!!')

import GET
print('[BOOT] \'GET\' imported')

import Wifi
print('[BOOT] \'Wifi\' imported')

import uasyncio as asyncio
print('[BOOT] \'asyncio\' imported')

import utime as time
print('[BOOT] \'time\' imported')


if asyncio.run(Wifi.connectWIFI()):
    print('[BOOT] WIFI connected!!')
    
    import UDP
    print('[BOOT] \'UDP\' imported')

else:
    print('[BOOT][ERROR] bad WIFI connection...')
    print('[BOOT][ERROR] reboot in 5 seconds')
    time.sleep(5)
    import machine
    machine.reset()
