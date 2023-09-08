from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.app.wsgi import WSGIApplication

from ryu.lib.packet import ethernet
from ryu.lib.packet import packet
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib.packet import icmp
from ryu.lib.packet import ether_types

from ryu.topology import event

from custom_controller_rest import MyControllerRest

import logging
import networkx as nx

import pickle

class MyController( app_manager.RyuApp ):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    _CONTEXTS = {'wsgi': WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(MyController, self).__init__(*args, **kwargs)
        wsgi = kwargs['wsgi']
        wsgi.register(controller=MyControllerRest, data={'my_controller': self})

        self.switches = list()
        self.links = list()
        self.hosts = list()
        self.mac_to_port = dict()

        self.net = nx.DiGraph()

        self.logger.setLevel(logging.DEBUG)
        FileOutputHandler = logging.FileHandler('logs.log')
        self.logger.addHandler(FileOutputHandler)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(port=ofproto.OFPP_CONTROLLER, max_len=ofproto.OFPCML_NO_BUFFER)]  #parser.OFPActionOutput(ofproto.OFPP_FLOOD),
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        instructions = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions=actions)]
        flow_mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=instructions)
        datapath.send_msg(flow_mod)


    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        datapath = ev.msg.datapath
        in_port = ev.msg.match['in_port']
        pkt = packet.Packet(data=ev.msg.data)

        pkt_ethernet = pkt.get_protocol(ethernet.ethernet)

        if not pkt_ethernet:
            return 
        
        if pkt_ethernet.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
       
        pkt_arp = pkt.get_protocol(arp.arp)
        
        if pkt_arp:
            self._handle_arp(datapath, in_port, pkt_ethernet, pkt_arp)
            return

        pkt_ipv4 =  pkt.get_protocol(ipv4.ipv4)
        pkt_icmp = pkt.get_protocol(icmp.icmp)

        if pkt_icmp:
            self._handle_icmp(datapath, in_port, pkt_ethernet, pkt_ipv4, pkt_icmp)
            return
    
        
    def _handle_arp(self, datapath, port, pkt_ethernet, pkt_arp):
        # if pkt_arp.opcode != arp.ARP_REQUEST:
        #     self.logger.warning('\n opcode != ARP_REQUEST, opcode = %s, ARP_REQUEST = %s \n' %(pkt_arp.opcode, arp.ARP_REQUEST))
        #     return 

        pkt = packet.Packet()
        pkt.add_protocol(ethernet.ethernet(ethertype=pkt_ethernet.ethertype, dst=pkt_ethernet.dst, src=pkt_ethernet.src))
        pkt.add_protocol(arp.arp(opcode=arp.ARP_REPLY, src_mac=pkt_arp.src_mac, src_ip=pkt_arp.src_ip, dst_mac=pkt_arp.dst_mac, dst_ip=pkt_arp.dst_ip))

        #get dst from ethernet packet.
        dst = pkt_ethernet.dst
        src = pkt_ethernet.src

        out_port = self._mac_port_table_lookup(datapath, src, dst, port)

        self._send_packet(datapath, port, out_port, pkt, dst, src)

    def _handle_icmp(self, datapath, port, pkt_ethernet, pkt_ipv4, pkt_icmp):
        # if pkt_icmp.type != icmp.ICMP_ECHO_REQUEST:
        #     self.logger.warning('\n icmp.type != ICMP_ECHO_REQUEST, icmp.type = %s, ICMP_ECHO_REQUEST = %s \n' %(pkt_icmp.type, icmp.ICMP_ECHO_REQUEST))
        #     return 

        pkt = packet.Packet()
        
        pkt.add_protocol(ethernet.ethernet(ethertype=pkt_ethernet.ethertype, dst=pkt_ethernet.dst, src=pkt_ethernet.src))
        pkt.add_protocol(ipv4.ipv4(dst=pkt_ipv4.dst, src=pkt_ipv4.src, proto=pkt_ipv4.proto))
        pkt.add_protocol(icmp.icmp(type_=icmp.ICMP_ECHO_REPLY, code=icmp.ICMP_ECHO_REPLY_CODE, csum=0, data=pkt_icmp.data))

        dst = pkt_ethernet.dst
        src = pkt_ethernet.src
        out_port = self._mac_port_table_lookup(datapath, src, dst, port)

        self._send_packet(datapath, port, out_port, pkt, dst, src)

    def _mac_port_table_lookup(self, datapath, src, dst, port):
        """
            return outport and update mac-port table
        """

        # store self.net object to visualize later 
        # with open('netxG.pkl', 'wb') as f:
        #     pickle.dump(self.net, f)

        if dst in self.net:
            path = nx.shortest_path(self.net,src,dst) # get shortest path
        else:
            out_port = ofproto_v1_3.OFPP_FLOOD
            return out_port
        
        next_node = path[path.index(datapath.id)+1] #next hop. starting from node after switch connected to src host on the path array
        if isinstance(next_node, int): #if it's an int, then it is leading to a different switch. the int represents a dpid
            #as a result, all we have to do is to find the link that has the src dpid value as our current dpid value and the dst dpid value as the current_next node value
            link = [link for link in self.links if link.src.dpid == datapath.id and link.dst.dpid == next_node]  #to be optimized : )
            out_port_key = link[0].dst.hw_addr 
            if out_port_key in self.mac_to_port[datapath.id].keys():
                return self.mac_to_port[datapath.id][out_port_key] #outport
        elif isinstance(next_node, str):
            out_port = self.mac_to_port[datapath.id][next_node]
            return out_port

    def _send_packet(self, datapath, in_port, out_port, pkt, dst, src):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        pkt.serialize()
        
        data = pkt.data
        actions = [parser.OFPActionOutput(port=out_port)]

        #install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            self.add_flow(datapath=datapath, priority=1, match=match, actions=actions)
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=data)
            datapath.send_msg(out)
            return

        else: #initial flooding as the flow table get's updated, we wont need to flood anymore.

            # instead of just plain up flooding all the ports, 
            # what I did was to extract all the ports except the in-port and the controller 
            # and send all the packets manually to those ports .
            out_ports = []
            for port in self.mac_to_port[datapath.id].values():
                if port != in_port and port != ofproto.OFPP_CONTROLLER:
                    out_ports.append(port)

            for port in out_ports:
                actions = [parser.OFPActionOutput(port=port)]
                out = parser.OFPPacketOut(datapath=datapath, buffer_id=ofproto.OFP_NO_BUFFER, in_port=in_port, actions=actions, data=data)
                datapath.send_msg(out)

            return
    
    #get the switches
    @set_ev_cls(event.EventSwitchEnter)
    def _get_switches(self, ev):
        self.switches.append(ev.switch) #to be sorted (for efficient searching)
        self.mac_to_port.setdefault(ev.switch.dp.id, {})
        
        #add switch to netx object
        self.net.add_node(ev.switch.dp.id)

    #get the links between dem switches
    @set_ev_cls(event.EventLinkAdd)
    def _get_links(self, ev):
        self.links.append(ev.link) #to be sorted (for efficient searching)
        self.mac_to_port[ev.link.src.dpid][ev.link.dst.hw_addr] = ev.link.src.port_no
        
        #link switches in netx object
        self.net.add_edge(u_of_edge=ev.link.src.dpid, v_of_edge=ev.link.dst.dpid)

    #get the hosts.
    @set_ev_cls(event.EventHostAdd)
    def _get_hosts(self, ev):
        self.hosts.append(ev.host.mac) #to be sorted (for efficient searching)
        self.mac_to_port[ev.host.port.dpid][ev.host.mac] = ev.host.port.port_no

        #add host to netx object
        self.net.add_node(ev.host.mac)

        #bi-directional linking
        self.net.add_edge(u_of_edge=ev.host.mac, v_of_edge=ev.host.port.dpid)
        self.net.add_edge(v_of_edge=ev.host.mac, u_of_edge=ev.host.port.dpid)
        

if __name__ == '__main__':
    from ryu import cfg
    cfg.CONF(args=[__file__, '--ofp-tcp-listen-port', '6653'], project='ryu')
    app_manager.main()

    #app_manager.require_app('ryu.controller.ofp_handler', api_style=True)



