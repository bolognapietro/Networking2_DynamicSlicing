#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink, TCIntf

from os import system
import re
import socket
import json
from time import sleep

import params

def mapNetwork(net: Mininet):

    network_map = []
    processed_pairs = []

    speed_tag = ["","K","M","G","T"]

    to_float = lambda x: float(re.sub(r'[^\d.]+','', str(x)))
    def to_bps(bandwidth: str):
        speed_tag = ["b","K","M","G","T"]

        bandwidth_value, bandwidth_tag = bandwidth.split(" ")
        bandwidth_value = to_float(bandwidth_value)
        bandwidth_tag = bandwidth_tag[0]

        if bandwidth_tag not in speed_tag:
            raise ValueError("Unsopported bandwidth unit")
        
        bandwidth_tag = speed_tag.index(bandwidth_tag)
        bandwidth_value = bandwidth_value * (1000 ** bandwidth_tag)
        
        return bandwidth_value

    # Get host pairs
    for node in net.hosts:
        
        for dest in net.hosts:
            
            if node == dest:
                continue

            node_tag = int(re.sub('[^0-9]','', node.name))
            dest_tag = int(re.sub('[^0-9]','', dest.name))

            pair = f"{node.name}-{dest.name}" if node_tag < dest_tag else f"{dest.name}-{node.name}"

            if pair in processed_pairs:
                continue

            processed_pairs.append(pair)

            result = net.ping([node, dest],timeout="0.5")

            if result == 100:
                continue
            
            # Ping host1 - host2 and viceversa. Then, calculate the average speed of each host
            server, client = net.iperf(hosts=[node, dest], seconds=1)

            server1 = to_bps(server)
            client1 = to_bps(client)
            
            client, server = net.iperf(hosts=[dest, node], seconds=1)

            server2 = to_bps(server)
            client2 = to_bps(client)

            server = round((server1 + server2)/2,2)
            server_value = round(server / (1000 ** (len(str(int(server))) % 4)),2)
            server_str = f"{server_value} {speed_tag[len(str(int(server))) % 4]}bits/sec"

            client = round((client1 + client2)/2,2)
            client_value = round(client / (1000 ** (len(str(int(client))) % 4)),2)
            client_str = f"{client_value} {speed_tag[len(str(int(client))) % 4]}bits/sec"

            # Add items to the network map
            network_map.append({
                "host1": {
                    "name": node.name,
                    "speed_value": server_value,
                    "speed_str": server_str,
                    #"node": node
                },

                "host2": {
                    "name": dest.name,
                    "speed_value": client_value,
                    "speed_str": client_str,
                    #"node": dest
                }
            })

    return network_map
        
class Interface():

    def __init__(self, interface: TCIntf) -> None:
        self.interface = interface

        self.ip = interface.ip
        self.mac = interface.mac
        self.nameToIntf = interface.name
        self.name = interface.node.name

class Link():

    def __init__(self, interface1: Interface, interface2: Interface) -> None:
        self.interface1 = interface1
        self.interface2 = interface2

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

    #system("clear")

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

    #system("clear")


    if __name__ == "__main__":
        CLI(net)
    else:

        # This socket allows the master to send commands coming from outside the VM
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((params.BRIDGE_HOST, params.BRIDGE_PORT))
        s.listen(1)

        while True:

            # Wait for a new connection
            connection, addr = s.accept()

            # Wait for a valid command
            data = connection.recv(1024)

            if not data:
                continue

            command = data.decode()

            # Parse command
            if command == "mapNetwork":
                network_map = mapNetwork(net)
                network_map = json.dumps(network_map)
                connection.sendall(network_map.encode())

    # Stop
    net.stop()

    # Clear
    system("sudo mn -c && clear")

if __name__ == "__main__":
    start()
