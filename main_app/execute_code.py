import subprocess, threading
import os, re


def findMainClass(code):
    data = re.split('{|}', code)
    index = -1
    for i in range(len(data)):
        if "public static void main" in data[i]:
            index = i - 1

    if index == -1:
        return None
    className = data[index].split()[-1].replace("{", "").replace(" ", "")
    return className


def run_command_with_timeout(cmd, timeout_sec, lang):
    f = open("code." + lang, "w")
    f.write(cmd)
    f.close()

    proc = None
    if lang == "py":
        proc = subprocess.Popen("wsl cat code.py | timeout 3s python3", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif lang == "cpp":
        proc = subprocess.Popen("wsl g++ code.cpp -o test ;timeout 3s ./test", stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
    elif lang == "java":
        class_name = findMainClass(cmd)
        if class_name is None:
            if os.path.isfile("code." + lang):
                os.remove("code." + lang)
            return (1, "Main class not found")
        proc = subprocess.Popen(f"wsl javac code.java; timeout 3s java {class_name}", stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

    timer = threading.Timer(timeout_sec, proc.kill)
    timer.start()
    out, err = proc.communicate()
    if os.path.isfile("code." + lang):
        os.remove("code." + lang)
    if timer.is_alive():
        timer.cancel()
        if os.path.isfile("test"):
            os.remove("test")
        os.system("rm *.class -f")
        return (0, (out, err))

    return (1, "Process killed: program cannot run for more than 3 secs.")


def run_python(code, timeout=3):
    a = run_command_with_timeout(code, timeout, "py")

    if (a[0] == 1):
        return str(a[1])
    if (a[0] == 0):
        output = str(a[1][0])[2:-1]
        error = str(a[1][1])[2:-1]
        if output == '':
            return error
        else:
            return output


def run_cpp(code, timeout=3):
    a = run_command_with_timeout(code, timeout, "cpp")
    if (a[0] == 1):
        return str(a[1])
    if (a[0] == 0):
        output = str(a[1][0])[2:-1]
        error = str(a[1][1])[2:-1]
        if output == '':
            return error
        else:
            return output


def run_java(code, timeout=3):
    a = run_command_with_timeout(code, timeout, "java")

    if a[0] == 1:
        return str(a[1])
    output = str(a[1][0])[2:-1]
    error = str(a[1][1])[2:-1]
    if (a[0] == 0):
        if output == '':
            return error
        else:
            return output


print(run_java("""
class Cls2{

    int x = 55;

}

class Cls1{

int j= 5;
}

"""))

# print(run_java("""
# class Cls1{

# public static void main(String[] args){

# 	    for(int i = 0; i<5; i++)
# 	        System.out.println(i);

# }}
# """))

# print(run_java("""
# class Cls1{

# public static void main(String[] args){

# 	System.out.println("Hello World!");
# }

# }
# """))


# print(run_cpp("""
# #include "iostream"
# // demo2.C - Sample C++ program
# int main(void)
# {
#     std::cout << "Hello! This is a C++ program."<<endl;
#     return 0;
# }
# """))

# print(run_python("print('Hello world')"))
