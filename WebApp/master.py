import socket
from time import sleep
import paramiko

SSH_HOST = "localhost"
SSH_USERNAME = "comnetsemu"
SSH_PASSWORD = "comnetsemu"
SSH_PORT = 2222

SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 2223

LAUNCHER_PATH = "<LAUNCHER PATH>"

def connect():

    global SOCKET_HOST, SOCKET_PORT

    # Connect to mininet socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SOCKET_HOST, SOCKET_PORT))
    
    return s

def disconnect(s: socket.socket):

    # Disconnect
    s.close()

def send(s: socket.socket, message: str, wait: bool = False):

    # Send message
    message = f"{message}"
    s.sendall(message.encode())

    if wait: # If True, it will wait until an ack is received
        s.recv(1024)

def isConnected(s: socket.socket):

    # Test connection with the mininet socket
    try:
        send(s,f"ping",True)
        return True
    except Exception as e:
        return False
    
def _exec_command(s: socket.socket, command: str):

    global SSH_HOST, SSH_USERNAME, SSH_PASSWORD, SSH_PORT

    # Parse command

    if command == "start":
        
        # If connected, return
        if isConnected(s):
            return
        
        disconnect(s)

        # Since the mininet socket isn't running, we establish a connection with the VM via ssh
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SSH_HOST, username=SSH_USERNAME, password=SSH_PASSWORD, port=SSH_PORT)

        # Execute launcher.py (start mininet network)
        ssh.exec_command(f"sudo python3 {LAUNCHER_PATH} &")
        ssh.close()
        
        # Wait for the mininet socket
        while True:
            s = connect()

            if isConnected(s):
                break

            disconnect(s)
            sleep(1)

        # Commands sequence terminated
        send(s,"#")

    elif command == "stop":

        # If not connected, return
        if not isConnected(s):
            return

        # Send stop message
        send(s,"stop",True)

        # Wait until disconnected
        while isConnected(s):
            sleep(1)
        
    elif command == "ping":

        # Ping connection
        result = str(isConnected(s)).lower()

        if result == "true":
            send(s,"#")

        return result
    
    elif command.startswith("changeScenario="):
        
        # Change scenario
        args = command.replace("changeScenario=","")
        
        # Check if the provided scenario id is valid
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

        # If not connected return
        if not isConnected(s):
            return ""
        
        send(s,"mapNetworkScenarios")

        # Since the network map can have an high size, 
        # the reading of a message is set to non blocking.
        # In this way it's possible to receive data and stop once a message 
        # is followed by an exception (empty buffer, there is no data to read)

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

    try:
        s = connect()
        result = _exec_command(s,command)
        disconnect(s) # Disconnect once finished

    except ConnectionRefusedError:
        result = "-" # VM not started
        
    except Exception as e:
        print(e) # For debug
        result = "-"
    
    return result
