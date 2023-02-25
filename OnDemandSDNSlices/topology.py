#!/usr/bin/python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

from os import system

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

if __name__ == "__main__":

    system("clear")

    net = Mininet(
        topo=NetworkTopology(),
        switch=OVSKernelSwitch,
        controller=RemoteController("c1", ip="127.0.0.1", port=6633),
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )

    net.build()
    net.start()
    CLI(net)
    net.stop()

    system("sudo mn -c && clear")
