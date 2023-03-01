import socket
from time import sleep
import paramiko
from os.path import join

SSH_HOST = "localhost"
SSH_USERNAME = "comnetsemu"
SSH_PASSWORD = "comnetsemu"
SSH_PORT = 2222

SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 2223

LAUNCHER_PATH = "/home/comnetsemu/chri/OnDemandSDNSlices/launcher.py"

def connect():

    global SOCKET_HOST, SOCKET_PORT

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SOCKET_HOST, SOCKET_PORT))
    
    return s

def disconnect(s: socket.socket):

    try:
        s.close()
    except:
        pass

def send(s: socket.socket, message: str, wait: bool = False):

    message = f"{message}"
    s.sendall(message.encode())

    if wait:
        s.recv(1024)

def isConnected(s: socket.socket):

    try:
        send(s,f"ping",True)
        return True
    except Exception as e:
        return False
    
def _exec_command(s: socket.socket, command: str):

    global SSH_HOST, SSH_USERNAME, SSH_PASSWORD, SSH_PORT

    if command == "start":
        
        if isConnected(s):
            return
        
        disconnect(s)

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USERNAME, password=SSH_PASSWORD, port=SSH_PORT)
        ssh.exec_command(f"sudo python3 {LAUNCHER_PATH} &")
        ssh.close()
        
        while True:
            s = connect()

            if isConnected(s):
                break

            disconnect(s)
            sleep(1)

        send(s,"#")

    elif command == "stop":

        if not isConnected(s):
            return

        send(s,"stop",True)

        while isConnected(s):
            sleep(1)
        
    elif command == "ping":

        result = str(isConnected(s)).lower()

        if result == "true":
            send(s,"#")

        return result
    
    elif command.startswith("changeScenario="):
        
        args = command.replace("changeScenario=","")
        
        if type(args) == str:
            if not args.isnumeric():
                return
        elif type(args) != int:
            return
        
        if int(args) not in range(0,5):
            return

        if not isConnected(s):
            return
        
        send(s,f"scenarioId={args[0]}",True)
        send(s,"#")

    elif command == "mapNetworkScenarios":

        if not isConnected(s):
            return ""
        
        send(s,"mapNetworkScenarios")
        s.setblocking(0)

        # Wait for response
        prev = False
        result = ""

        while True:

            try:
                data = s.recv(1024)
            except BlockingIOError: # No data available
                
                # Close if i have already read something
                if prev: 
                    break

                sleep(0.5)
                continue
            
            # Store all the received data
            if len(data.decode()):
                result = result + data.decode()
                prev = True
        
        send(s,"#")
        return result

def exec_command(command: str):

    s = connect()
    result = _exec_command(s,command)
    disconnect(s)
    
    return result


