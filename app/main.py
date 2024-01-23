from fastapi import FastAPI
from pydantic import BaseModel
import socketio

import subprocess, shlex, time

app = FastAPI()

#Socket io (sio) create a Socket.IO server
sio=socketio.AsyncServer(cors_allowed_origins="*",async_mode='asgi',logger=True)

socket_app = socketio.ASGIApp(sio)
app.mount("/ml_compile", socket_app) #add socket.io router

class Code(BaseModel):
    lang: str
    code: str
    input: str

@app.get("/")
def root():
    return {"title":"Compiler API"}

@app.post('/compile')
def compile_code(code:Code):
    if code.lang == 'python':
        timestamp = int(time.clock_gettime(1)) # make Timestamp
        file_name = timestamp + "_py" +'.py'
        with open(file=file_name, mode="w") as f:
            f.write(code) # write code to file
        command_line = 'python3 ' + file_name #make cmd line to run python script
        args = shlex.split(command_line)
        input_args = code.input.splitline() #split input str as line
        with subprocess.Popen(args, stdin=subprocess.PIPE,  stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc: #open shell & run code
            output : list = [] #make list for stdout
            for x in input_args:
                output.append(proc.communicate(input=x)) #PIPE communicate
            return {"output": output} #return stdout

@sio.on("connect")
async def connect(sid, msg):
    print("New Client Connected to This id :"+" "+str(sid))


"""
socket.io in "compile_ml"
1. msg는 dict구조로 이루어져 있음. 다음과 같은 구조로 서버에 보낸다.
    - lang
    - code
2. join -> connect -> compile_ml -> disconnect의 라우팅 과정을 거친다.
"""

@sio.on("compile_ml")
async def compile_ml(sid, msg):
    if msg['lang'] == 'python':
        timestamp = int(time.clock_gettime(1)) # make Timestamp
        file_name = timestamp + "_ml" + '.py'
        with open(file=file_name, mode="w") as f:
            f.write(msg['code']) # write code to file
        command_line = 'python3 ' + file_name #make cmd line to run python script
        args = shlex.split(command_line)
        with subprocess.Popen(args, stdin=subprocess.PIPE,  stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc: #open shell & run code
            sio.send()


"""
TODO
1. make room code
"""
