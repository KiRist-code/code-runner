import subprocess, shlex, time, json

def newline_split(s:str):
    ret : list = []
    for line in s.split("\n"):
        ret.append(line)
    return ret

def pipe_run(args:list[str], input_args:list[str]):
    with subprocess.Popen(args, stdin=subprocess.PIPE,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', text=True) as proc: #open shell & run code
        output : list = [] #make list for stdout
        if not input_args:
            stdout, stderr = proc.communicate(timeout=10) #PIPE communicate
            output = newline_split(stdout)
            err = newline_split(stderr)
        else:
            for x in input_args:
                stdout, stderr = proc.communicate(input=bytes(x, 'utf-8'),timeout=5)#PIPE communicate
                output.extend(newline_split(stdout))
                err.extend(newline_split(stderr))
        return {"output": output, "error": err} #return stdout
    