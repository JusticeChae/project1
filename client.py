import asyncio
import socketio
from flask_socketio import send, emit
import threading
import time

# plot
import numpy as np
import matplotlib.pyplot as plt

sio = socketio.AsyncClient()

@sio.event()
async def connect():
    print('connection established')

@sio.event()
async def disconnect():
    print('disconnected from server')

@sio.event()
async def my_message(data):
    print('message received with', data)
    await sio.emit('my_message', {'response': 'my response'})

chk = True
x = 0
@sio.on('response')
async def response(data):
    global chk, x
    print(data)
    if data == 'bye':
        chk = False
    else:
        x = x + 0.1
        y = np.sin(x)

        plt.scatter(x,y)
        plt.pause(0.0001)
    
test_json = {
    'DATA_TYPE':'report',
    'AGV_NO':'AGV00001',
    'LOCATION':'00010002',
    'STATE':'1',
    'MODE':'1',
    'DIRECTION':'0',
    'MAX_VELOCITY':'2.5',
    'TILT_MAX_ANGLE':'20',
    'BELT_MAX_SPEED':'1.5',
    'COMMAND_WAIT_TIME':'10',
    'MIN_VOLTAGE':'15.6',
    'BATTERY_LVL':'30',
    'AGV_FIRMWARE_VERSION':'1.01'
}

async def main():
    global chk
    '''
    def send_state():
        async def async_send_state():
        while True:
            async_send_state()
    t = threading.Thread(target=send_state)
    t.start()
    '''
    await sio.connect('http://127.0.0.1:5000')
    while True:
        await sio.emit('status',test_json)
        await asyncio.sleep(1)
        if chk == False:
            break
        #temp = input('>>')
        #if temp == '1':
            #t.join()
        #    break
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())