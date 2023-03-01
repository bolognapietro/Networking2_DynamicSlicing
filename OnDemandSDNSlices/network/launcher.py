import socket
import subprocess
from time import sleep
from os import system

import topology
import params

def launch():

    # Close previous socket (if any)
    while True:

        output = subprocess.Popen(f"sudo lsof -i:{params.BRIDGE_PORT}", shell=True, stdout=subprocess.PIPE).communicate()[0].decode()

        if len(output):
            output = output.split("\n")[1:-1]
            
            for o in output:
                o = [item for item in o.split(" ") if len(item)]
                pid = o[1]

                if not pid.isnumeric():
                    continue

                system(f"kill -9 {pid}")
        else:
            break

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

if __name__ == "__main__":
    launch()
