import subprocess, shlex, time, json

def pipe_run(args:list[str], input_args:list[str]):
    with subprocess.Popen(args, stdin=subprocess.PIPE,  stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc: #open shell & run code
        output : list = [] #make list for stdout
        if not input_args:
            output.append(proc.communicate()) #PIPE communicate
        else:
            for x in input_args:
                output.append(proc.communicate(input=bytes(x, 'utf-8'))) #PIPE communicate
        return {"output": output} #return stdout