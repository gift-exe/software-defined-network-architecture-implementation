from operator import attrgetter

from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.controller import ofp_event

from ryu.lib import hub

from custom_controller import MyController

class MyControllerMonitor(MyController):
    def __init__(self, *args, **kwargs):
        super(MyControllerMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('\nREGISTER datapath %016x \n', datapath.id)    
                self.datapaths[datapath.id] = datapath

        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('\nDELETING datapath %016x \n', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)
    
    def _request_stats(self, datapath):
        self.logger.debug('\nSENDING STATS REQUEST: %016x \n', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        request = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(request)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('\nFLOW STATS')

        self.logger.info('\ndatapath         '
                         'in-port  eth-dst           '
                         'out-port packets  bytes')
        self.logger.info('---------------- '
                         '-------- ----------------- '
                         '-------- -------- --------')
        
        for stat in sorted([flow for flow in body if flow.priority == 1], 
                           key=lambda flow: (flow.match['in_port'], 
                                             flow.match['eth_dst'])):
            
            self.logger.info('%016x %8x %17s %8x %8d %8d',
                             ev.msg.datapath.id, stat.match['in_port'],
                             stat.match['eth_dst'], stat.instructions[0].actions[0].port,
                             stat.packet_count, stat.byte_count)
        
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body

        self.logger.info('\nPORTS STATS')

        self.logger.info('\ndatapath         port     '
                         'rx-pkts  rx-bytes rx-error '
                         'tx-pkts  tx-bytes tx-error')
        self.logger.info('---------------- -------- '
                         '-------- -------- -------- '
                         '-------- -------- --------')
        
        for stat in sorted(body, key=attrgetter('port_no')):
            self.logger.info('%016x %8x %8d %8d %8d %8d %8d', 
                             ev.msg.datapath.id, stat.port_no, 
                             stat.rx_packets, stat.rx_bytes, stat.tx_errors, 
                             stat.tx_packets, stat.tx_bytes, stat.tx_errors)
