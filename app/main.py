from fastapi import FastAPI
from pydantic import BaseModel

import subprocess, shlex, time

app = FastAPI()

class Code(BaseModel):
    lang: str
    code: str
    input: str

@app.post('/compile')
def compile_code(code:Code):
    if code.lang == 'Python':
        timestamp = int(time.clock_gettime(1)) # make Timestamp
        file_name = timestamp + '.py'
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

