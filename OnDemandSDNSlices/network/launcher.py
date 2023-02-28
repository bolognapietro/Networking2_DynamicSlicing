import socket
import subprocess
from time import sleep

import topology
import params

# Clear
process = subprocess.Popen("sudo mn -c", shell=True, stdout=subprocess.PIPE)
process.wait()

# Start controller
process = subprocess.Popen(f"ryu-manager {params.CONTROLLER_PATH}", shell=True, stdout=subprocess.PIPE)

# Wait until controller is ready
while True:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((params.CONTROLLER_IP,params.CONTROLLER_PORT))

    if not result:
        break

    sleep(0.5)

# Start mininet
topology.start()


