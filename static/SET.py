from utime import time
import json

def setTimeOffset():
    with open('./timeOffset.txt', 'w') as to:
        to.write(str(time()))
        
        
async def setIsOnline(value):
    with open('./status.json', 'r') as status:
        _json = json.load(status)
    
    _json['isOnline'] = value
    
    with open('./status.json', 'w') as status:
        json.dump(_json, status)
                
                
async def setIsLight(value):
    with open('./status.json', 'r') as status:
        _json = json.load(status)
    
    _json['isLight'] = value
    
    with open('./status.json', 'w') as status:
        json.dump(_json, status)
        
        
async def setIsSetColor(value):
    with open('./status.json', 'r') as status:
        _json = json.load(status)
    
    _json['isSetColor'] = value
    
    with open('./status.json', 'w') as status:
        json.dump(_json, status)


async def setColor(rgb):
    with open('./status.json', 'r') as status:
        _json = json.load(status)
    
    _json['Color'] = rgb
    
    with open('./status.json', 'w') as status:
        json.dump(_json, status)
        

async def setOriginalColor(rgb):
    with open('./status.json', 'r') as status:
        _json = json.load(status)
    
    if not _json['isSetColor']:
        _json['Color'] = rgb
    _json['_Color'] = rgb
    
    with open('./status.json', 'w') as status:
        json.dump(_json, status)

        
async def setID(id):
    with open('./id', 'r') as ID:
        _id = ID.read()
    
    with open('./_id', 'w') as _ID:
        _ID.write(_id)
        
    with open('./id', 'w') as ID:
        ID.write(id)