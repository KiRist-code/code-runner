from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

import subprocess, shlex, time, json
from pipe import pipe_run

app = FastAPI()

class Code(BaseModel):
    lang: str
    code: str
    input: List[str]

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
            f.write(code.code) # write code to file
        command_line = 'python3 ' + file_name #make cmd line to run python script
        args = shlex.split(command_line)
        input_args = code.input.splitlines() #split input str as line
        return pipe_run(args=args,input_args=input_args)
        
    if code.lang == 'Java': #Java 코드 컴파일
        timestamp = int(time.clock_gettime(1)) # make Timestamp
        with open(file="Main.java", mode="w") as f:
            f.write(code.code) # write code to file
        compile_command = "javac Main.java" #make cmd line to compile java script
        compile = shlex.split(compile_command)
        subprocess.Popen(args=compile)
        run_command= "java Main" #make cmd line to run java script
        args = shlex.split(run_command)
        input_args = code.input.splitlines() #split input str as line
        return pipe_run(args=args,input_args=input_args)
        

    else:
        return {"output": "", "error": "This language does not support."}
    


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
                    stdout, stderr = proc.communicate()
                    await manager.send_personal_message(stdout, websocket)
                await manager.send_personal_message("done", websocket=websocket)
                time.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print('Annonymous user left the ML compile route')

