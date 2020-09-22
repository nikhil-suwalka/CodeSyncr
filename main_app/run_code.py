import os


def run_python(source: str):
    return os.system('echo "'+source+'" | python ')


run_python("print('Hello world')")