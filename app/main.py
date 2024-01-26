from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import subprocess, shlex, time, json

app = FastAPI()

class Code(BaseModel):
    lang: str
    code: str
    input: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
def root():
    return {"title":"Compiler API"}

@app.post('/compile') #request body는 Code(BaseModel) 참고
def compile_code(code:Code):
    if code.lang == 'python': #Python 코드 컴파일
        timestamp = int(time.clock_gettime(1)) # make Timestamp
        file_name = str(timestamp) + "_py" +'.py'
        with open(file=file_name, mode="w") as f:
            f.write(code) # write code to file
        command_line = 'python3 ' + file_name #make cmd line to run python script
        args = shlex.split(command_line)
        input_args = code.input.splitline() #split input str as line

    if code.lang == 'Java': #Java 코드 컴파일
        timestamp = int(time.clock_gettime(1)) # make Timestamp
        file_name = str(timestamp) + "_java" +'.java'
        with open(file=file_name, mode="w") as f:
            f.write(code) # write code to file
        compile_command_line = 'javac -encoding UTF-8 ' + file_name #make cmd line to compile java script
        subprocess.run(compile_command_line)
        file_name.replace('.java', '') #delete extension file name to run as class
        run_command_line = f'java {file_name}' #make cmd line to run java script
        args = shlex.split(run_command_line)
        input_args = code.input.splitline() #split input str as line

    else:
        return {"output": "This language does not support."}

    with subprocess.Popen(args, stdin=subprocess.PIPE,  stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc: #open shell & run code
        output : list = [] #make list for stdout
        for x in input_args:
            output.append(proc.communicate(input=x)) #PIPE communicate
        return {"output": output} #return stdout


"""
websocket in "compile_ml"
1. msg는 json구조로 이루어져 있음. 다음과 같은 구조로 서버에 보낸다.
{
    "lang" : "ML",
    "code" : ""
}
"""

@app.websocket("/ws/compile_ml")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_text("Successfully Connected!")
    time.sleep(1)
    try:
        while True:
            text = await websocket.receive_text()
            data = json.loads(text) #json으로 직렬화
            if(data["lang"] == "ML"):
                timestamp = int(time.clock_gettime(1)) # make Timestamp
                file_name = str(timestamp) + "_ml" + '.py'
                with open(file=file_name, mode="w") as f:
                    f.write(data['code']) # write code to file
                command_line = 'python3 ' + file_name #make cmd line to run python script
                args = shlex.split(command_line)
                time.sleep(1)
                with subprocess.Popen(args, stdin=subprocess.PIPE,  stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc: #open shell & run code
                    await manager.send_personal_message(proc.communicate(), websocket)
                await manager.send_personal_message("done", websocket=websocket)
                time.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print('Annonymous user left the ML compile route')

