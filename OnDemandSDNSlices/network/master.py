import socket
import sys
from time import sleep

import params

# This script is called by the master outside the VM

if len(sys.argv) == 1:
    exit(0)

# Send command to topology.py 
command = sys.argv[1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((params.BRIDGE_HOST, params.BRIDGE_PORT))
s.sendall(command.encode())

s.setblocking(0)

# Wait for response
prev = False
result = ""

while True:

    try:
        data = s.recv(1024)
    except BlockingIOError: # Means that there is no data available
        
        # Close if i have already read something
        if prev: 
            break

        sleep(0.5)
        continue
    
    # Store all the received data
    if data != None:
        result = result + data.decode()
        prev = True


# Close socket
s.close()

# Return result
print(result)

