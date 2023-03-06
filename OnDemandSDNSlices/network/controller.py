from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.base import app_manager
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types

class TrafficSlicing(app_manager.RyuApp):

    # Specifies the supported OpenFlow version. In this case only 1.3
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)

        # Each MAC address is mapped to a specific port of each switch
        self.mac_to_port = {
            
            # Left end switch
            1: {
                "00:00:00:00:00:05": 5, 
                "00:00:00:00:00:01": 3, 
                "00:00:00:00:00:03": 4, 
                "00:00:00:00:00:07": 6,

                "00:00:00:00:00:06": 1,
                "00:00:00:00:00:02": 1,
                "00:00:00:00:00:04": 2, 
                "00:00:00:00:00:08": 2
            },

            # Upper middle switch
            2: {
                "00:00:00:00:00:05": 1,
                "00:00:00:00:00:01": 1, 

                "00:00:00:00:00:06": 2, 
                "00:00:00:00:00:02": 2
            },

            # Bottom middle switch
            3: {
                "00:00:00:00:00:03": 1, 
                "00:00:00:00:00:07": 1, 

                "00:00:00:00:00:04": 2, 
                "00:00:00:00:00:08": 2
            },

            # Right end switch
            4: {
                "00:00:00:00:00:05": 1, 
                "00:00:00:00:00:01": 1, 
                "00:00:00:00:00:03": 2, 
                "00:00:00:00:00:07": 2,

                "00:00:00:00:00:06": 5,
                "00:00:00:00:00:02": 3,
                "00:00:00:00:00:04": 4, 
                "00:00:00:00:00:08": 6
            },
        }

    # This function is called when the Ryu controller receives an EventOFPSwitchFeatures event from a switch
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev): 
        
        # ev is the EventOFPSwitchFeatures event received

        # Extract datapath objects from ev
        datapath = ev.msg.datapath

        # Extract OpenFlow version supported by the switch
        ofproto = datapath.ofproto #ryu.ofproto.ofproto_v1_3.OFP_VERSION

        # Extract the parser based on OpenFlow version
        parser = datapath.ofproto_parser #ryu.ofproto.ofproto_v1_3_parser

        # Creating a new OFPMatch object to match incoming packets based on the fields of the packet's header
        match = parser.OFPMatch()

        # Define a list of actions that are executed if the new flow entry is matched
        # In this case the packet is sent to the controller and the switch should not buffer the packet before sending it to the controller
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]

        # Add a new flow entry to the flow table of the switch
        self.add_flow(datapath, 0, match, actions)
    
    # This function adds a new flow entry to a switch using Openflow protocol
    def add_flow(self, datapath, priority, match, actions):

        # datapath is used to have a reference to the switch which wants to add a new flow entry to its flow table
        # priority defines the priority of the new flow entry. A higher priority indicates that the flow entry should be matched before lower priority entries in the flow table
        # math specifies the conditions under which the flow entry should be applied
        # actions specifies a list of actions to be executed if the flow entry is matched

        # Extract OpenFlow version supported by the switch
        ofproto = datapath.ofproto #ryu.ofproto.ofproto_v1_3.OFP_VERSION

        # Extract the parser based on OpenFlow version
        parser = datapath.ofproto_parser #ryu.ofproto.ofproto_v1_3_parser

        # Create a new OpenFlow OFPFlowMode message
        mod = parser.OFPFlowMod(
            datapath = datapath, # It's a reference to the switch
            priority = priority, # Priority of the new flow entry
            match = match, # Specifies the conditions under which the flow entry should be applied
            instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)] # Specifies a list of instructions to be executed if the flow entry is matched
        )

        # Sends the OFPFlowMod message to the switch
        datapath.send_msg(mod)

    # Send a packet to a switch and specify which is the output port
    def _send_package(self, msg, datapath, in_port, actions):
        
        # msg input message to be sent
        # datapath is used to have a reference to the switch which wants to add a new flow entry to its flow table
        # in_port specifies the input port of the switch that will receive the packet
        # actions specifies a list of actions to be executed if the flow entry is matched

        data = None

        # Check if the message has a buffer ID. If yes, assign the message's data to the variable data
        if msg.buffer_id == datapath.ofproto.OFP_NO_BUFFER:
            data = msg.data

        # Create a OFPPacketOut packet to be sent
        out = datapath.ofproto_parser.OFPPacketOut(
            datapath = datapath, # It's a reference to the switch
            buffer_id = msg.buffer_id, # Buffer ID if any, otherwise it will be datapath.ofproto.OFP_NO_BUFFER
            in_port = in_port, # Origin input port
            actions = actions, # Specifies a list of actions to be executed if the flow entry is matched
            data = data, # Packet's data
        )

        # Send the OFPPacketOut to the switch
        datapath.send_msg(out)

    # This function is called when the Ryu controller receives an EventOFPPacketIn event from a switch 
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        
        # ev is the EventOFPPacketIn event received

        # Extract the message inside the packet
        msg = ev.msg

        # Extract the datapath
        datapath = msg.datapath

        # Extract the input port
        in_port = msg.match["in_port"]

        # Create packet object from received message's data
        pkt = packet.Packet(msg.data)

        # Extract ethernet protocol from the packet
        eth = pkt.get_protocol(ethernet.ethernet)

        # Checks if ethernet frame type is LLDP
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        
        # Extract the destination MAC address
        dst = eth.dst

        # Extract the dpid of the switch
        dpid = datapath.id

        # Check if the destination MAC address is inside the dpid map of the mac_to_port table
        if dst in self.mac_to_port[dpid]: 

            # Extract the output port
            out_port = self.mac_to_port[dpid][dst]

            # Define a list of actions that are executed if the new flow entry is matched
            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

            # Creating a new OFPMatch object to match incoming packets based on the destination MAC address
            match = datapath.ofproto_parser.OFPMatch(eth_dst=dst)
            
            # Add a new flow entry to the flow table of the switch
            self.add_flow(datapath, 1, match, actions)

            # Send the packet
            self._send_package(msg, datapath, in_port, actions)
