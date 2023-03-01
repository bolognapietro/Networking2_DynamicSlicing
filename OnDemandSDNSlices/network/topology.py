#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink, TCIntf

from os import system
from os.path import join
import re
import socket
import json
from time import sleep
from threading import Thread
import subprocess

import params

CURRENT_SCENARIO = -1

def mapNetworkScenarios(net: Mininet, host_pairs: list = [["h1","h2"],["h3","h4"],["h5","h6"],["h7","h8"]]):

    global CURRENT_SCENARIO

    network_map = {"network": [], "scenario": CURRENT_SCENARIO}

    for pair in host_pairs:

        hosts = []

        for host in net.hosts:
            if host.name in pair:
                hosts.append(host)
        
        if len(hosts) != 2:
            continue

        h1, h2 = hosts

        result = net.ping([h1,h2],timeout="0.5")

        if result < 100:
            host1_speed, host2_speed = net.iperf(hosts=[h1, h2], seconds=1)

        else:
            host1_speed = "-"
            host2_speed = "-"
        
        # Add items to the network map
        network_map["network"].append({
            "host1": {
                "name": h1.name,
                "speed": host1_speed
            },

            "host2": {
                "name": h2.name,
                "speed": host2_speed
                #"node": dest
            }
        })
    
    return network_map

class NetworkTopology(Topo):
    
    def __init__(self):

        # Initialize topology
        Topo.__init__(self)

        # Create switch nodes
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        # Create host nodes
        for i in range(8):
            self.addHost("h%d" % (i + 1))

        #! The order is important since the links are created dynamically

        # Add switch links
        self.addLink('s1', 's2')
        self.addLink('s1', 's3')
        self.addLink('s2', 's4')
        self.addLink('s3', 's4')

        # Add host links
        self.addLink('h1', 's1')
        self.addLink('h2', 's4')
        self.addLink('h3', 's1')
        self.addLink('h4', 's4')
        self.addLink('h5', 's1')
        self.addLink('h6', 's4')
        self.addLink('h7', 's1')
        self.addLink('h8', 's4')

def start(controller: RemoteController = None):

    global CURRENT_SCENARIO

    system("clear")

    # Create control if it's None
    if controller == None:
        controller = RemoteController(params.CONTROLLER_NAME, ip=params.CONTROLLER_IP, port=params.CONTROLLER_PORT)

    # Create Mininet object
    print("[INFO] Creating Mininet object")

    net = Mininet(
        topo=NetworkTopology(),
        switch=OVSKernelSwitch,
        controller=controller,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )

    # Build
    print("[INFO] Building")
    net.build()

    # Start
    print("[INFO] Starting")
    net.start()

    system("clear")

    if __name__ == "__main__":
        CLI(net)

    else:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", params.BRIDGE_PORT))
        s.listen(1)
        
        run = True

        while run:

            # Wait for a new connection
            connection, addr = s.accept()
            chain = True

            while chain:
                
                # Wait for a valid command
                data = connection.recv(1024)

                if not len(data.decode()):
                    continue

                command = data.decode()

                if command == "#":
                    chain = False

                # Parse command
                if command == "mapNetworkScenarios":
                    network_map = mapNetworkScenarios(net)
                    network_map = json.dumps(network_map)
                    connection.sendall(network_map.encode())
                
                elif command.startswith("scenarioId="):
                    CURRENT_SCENARIO = int(command.replace("scenarioId=",""))

                    if CURRENT_SCENARIO == 0:
                        scenario = "default.sh"
                    elif CURRENT_SCENARIO == 1:
                        scenario = "scenarioUpper.sh"
                    elif CURRENT_SCENARIO == 2:
                        scenario = "scenarioLower.sh"
                    elif CURRENT_SCENARIO == 3:
                        scenario = "scenarioAll.sh"
                    elif CURRENT_SCENARIO == 4:
                        scenario = "scenarioBroken.sh"

                    process = subprocess.Popen(f"{join(params.SCENARIOS_PATH,scenario)}", shell=True, stdout=subprocess.PIPE)
                    process.wait()

                    connection.sendall("ack".encode())

                elif command == "stop":
                    connection.sendall("ack".encode())
                    run = False
                    break

                else:
                    connection.sendall("ack".encode())
        
        s.close()

    # Stop
    net.stop()

    # Clear
    system("sudo mn -c && clear")

if __name__ == "__main__":
    start()
