from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, send
from engineio.payload import Payload

Payload.max_decode_packets = 101
#Flask 객체 인스턴스 생성
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

@app.route('/',methods=('GET', 'POST')) # 접속하는 url
def index():
    if request.method == "POST":
        user = request.form.get('user')
        data = {'level': 60, 'point': 360, 'exp': 45000}
    return render_template('index.html', user=user, data=data)

count = 0
@socketio.on('connect')
def test_connect():
    global count
    print("socket connected")
    count = 0

@socketio.on('status')
def my_message(data):
    global count
    print('received message: ' + str(data))
    count += 1
    if count > 10:
        emit('response','bye')
    else:
        emit('response','hello')

if __name__=="__main__":
    socketio.run(app, debug=True)