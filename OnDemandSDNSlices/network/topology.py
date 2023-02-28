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

def mapNetworkScenarios(net: Mininet, host_pairs: list = [["h1","h2"],["h3","h4"],["h5","h6"],["h7","h8"]]):

    network_map = []
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

    for pair in host_pairs:

        hosts = []

        for host in net.hosts:
            if host.name in pair:
                hosts.append(host)
        
        if len(hosts) != 2:
            continue

        h1, h2 = hosts

        client, server = net.iperf(hosts=[h1, h2], seconds=1)

        server1 = to_bps(server)
        client1 = to_bps(client)
        
        client, server = net.iperf(hosts=[h2, h1], seconds=1)

        server2 = to_bps(server)
        client2 = to_bps(client)

        server = round((server1 + server2)/2,2)
        server_value = round(server,2)
        server_str = f"{round(server_value / (1000 ** (len(str(int(server))) % 4)),2)} {speed_tag[len(str(int(server))) % 4]}bits/sec"

        client = round((client1 + client2)/2,2)
        client_value = round(client, 2)
        client_str = f"{round(client_value / (1000 ** (len(str(int(client))) % 4)),2)} {speed_tag[len(str(int(client))) % 4]}bits/sec"
        
        # Add items to the network map
        network_map.append({
            "host1": {
                "name": h1.name,
                "speed_value": server_value,
                "speed_str": server_str,
                #"node": node
            },

            "host2": {
                "name": h2.name,
                "speed_value": client_value,
                "speed_str": client_str,
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

    system("clear")

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
            if command == "mapNetworkScenarios":
                network_map = mapNetworkScenarios(net)
                network_map = json.dumps(network_map)
                connection.sendall(network_map.encode())

    # Stop
    net.stop()

    # Clear
    system("sudo mn -c && clear")

if __name__ == "__main__":
    start()
