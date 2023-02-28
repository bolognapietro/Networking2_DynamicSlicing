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

# Wait for response
while True:
    result = s.recv(1024)

    if result != None:
        break

    sleep(0.5)

# Close socket
s.close()

# Return result
print(result)

