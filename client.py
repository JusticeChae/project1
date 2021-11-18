import asyncio
from os import name
import socketio
from flask_socketio import send, emit
import threading
import json
import time
import random

count = 0

move_data = {
    'DATA_TYPE': None,
    'AGV_NO': None,
    'ACTION': None,
    'BLOCKS': None
}

test_json = {
    # fix
    'DATA_TYPE': 'report',
    'AGV_NO': 'AGV00001',
    # nonfix
    'LOCATION': '00010002',
    'STATE': '1',
    'MODE': '1',
    'DIRECTION': '0',
    # fix
    'MAX_VELOCITY': '2.5',
    'TILT_MAX_ANGLE': '20',
    'BELT_MAX_SPEED': '1.5',
    'COMMAND_WAIT_TIME': '10',
    'MIN_VOLTAGE': '15.6',
    # nonfix
    'BATTERY_LVL': '30',
    # fix
    'AGV_FIRMWARE_VERSION': '1.01'
}
# 알람

alarm_json = {
    'DATA_TYPE': 'alarm',
    'AGV_NO': 'AGV0001',
    'ALARMS': [
        {
            'ALARM_CD': '11',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'Current location is not confirmed',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '12',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'After going straight, position error',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '13',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'After turning right 90 degrees, position error',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '14',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'After turning left 90 degrees, position error',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '15',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'After 180 degrees of rotation, position error',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '16',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'After reversing, position error',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '21',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'LOW BATTERY',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '22',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'Over-current occurs',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '31',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'Belt driving failed',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },
        {
            'ALARM_CD': '32',
            'ALARM_LVL': 'level',
            'ALARM_DTL': 'Failed to drive Tray',
            'ALARM_STATUS': '0',
            'OCCUR_DT': None,
            'END_DT': None
        },

    ]
}

sio = socketio.AsyncClient()

# 알람 전송


async def send_alarm():
    # 랜덤 ALARM_CD
    ALARM_CD_LIST = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    temp_alarm = random.choice(ALARM_CD_LIST)
    alarm_json['ALARMS'][temp_alarm]['ALARM_STATUS'] = 1
    alarm_json['ALARMS'][temp_alarm]['OCCUR_DT'] = time.strftime(
        '20%y%m%d %H:%M:%S')
    if(alarm_json['ALARMS'][temp_alarm]['END_DT'] is not None):
        alarm_json['ALARMS'][temp_alarm]['END_DT'] is None
    await sio.emit('alarm', json.dumps(alarm_json))
    await asyncio.sleep(4)
    alarm_json['ALARMS'][temp_alarm]['END_DT'] = time.strftime(
        '20%y%m%d %H:%M:%S')
    alarm_json['ALARMS'][temp_alarm]['ALARM_STATUS'] = 0


# connect되면 알람 발생
@sio.event
async def connect():
    while True:
        await send_alarm()
        await sio.sleep(1)


# AGV 상태요청 receive

@sio.on('state')
async def state(data):
    json_data = json.loads(data)

    # 상태보고 전송 Thread 시작
    if json_data['DATA_TYPE'] == 'reportRqst':
        await sio.sleep(1)
        sio.start_background_task(send_state)

# AGV 상태보고 전송


async def send_state():
    while True:
        await sio.emit('state', json.dumps(test_json))
        await sio.sleep(3)

# AGV 이동 명령 receive


@sio.on('move')
async def move_avg(data):
    move_data = json.loads(data)
    global count
    if(move_data['BLOCKS'] is not None):
        test_json['LOCATION'] = move_data['BLOCKS'][count]
        count = + 1
    print(move_data)

# 서버 연결 해제


@sio.event()
async def disconnect():
    print('disconnected from server')


async def main():
    # local
    await sio.connect('http://127.0.0.1:5000', headers={'AGV_NO': 'AGV00001'})
    # aws ec2
    # await sio.connect('http://13.124.72.207:5000', headers={'AGV_NO': 'AGV00001'})
    await sio.wait()

if __name__ == '__main__':
    asyncio.run(main())
