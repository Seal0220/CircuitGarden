import json
from utime import time


async def getPassword():
    with open('./IPs.json', 'r') as Json:
        _json = json.load(Json)
        
    _password = _json['Password']
    
    return _password


async def getIPconfig():
    with open('./IPs.json', 'r') as Json:
        _json = json.load(Json)
    
    _SSID = _json['SSID']
    _IP = _json['IP'] + await getID()
    _SubnetMask = _json['SubnetMask']
    _Gateway = _json['Gateway']
    _DNS = _json['DNS']
    _port = _json['Port']
    
    return _SSID, _IP, _SubnetMask, _Gateway, _DNS, _port


async def getIPHead():
    with open('./IPs.json', 'r') as Json:
        _json = json.load(Json)
        
    _IPHead = _json['IP']
    
    return _IPHead


async def getID():
    with open('./id', 'r') as _ID:
        return _ID.read()
    

async def getGroup(_ID):
    with open('./IPs.json', 'r') as Json:
        _json = json.load(Json)
        
    _Groups = _json['Groups']
    for group, content in _Groups.items():
        IDRange = content['ID']
        if IDRange[0] <= int(_ID) <= IDRange[1]:
            return group, IDRange, content['Color']
    
    
async def getTimeOffset():
     with open('./timeOffset.txt', 'r') as to:
        return int(to.read())
    

async def getTime():
    return time() - await getTimeOffset()


async def getIsOnline():
    with open('./status.json', 'r') as status:
        _json = json.load(status)
        
    return _json['isOnline']


async def getIsLight():
    with open('./status.json', 'r') as status:
        _json = json.load(status)
        
    return _json['isLight']


async def getIsSetColor():
    with open('./status.json', 'r') as status:
        _json = json.load(status)
        
    return _json['isSetColor']


async def getHostIP():
    with open('./IPs.json', 'r') as Json:
        _json = json.load(Json)
    
    hostIPs = []
    for host in _json['Host']:
        hostIPs.append(host['IP'])
    return hostIPs


async def getColor():
    with open('./status.json', 'r') as status:
        _json = json.load(status)
        
    return _json['Color']


async def getOriginalColor():
    with open('./status.json', 'r') as status:
        _json = json.load(status)
        
    return _json['_Color']
