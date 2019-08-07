from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.recoco import Timer
from collections import defaultdict
from pox.openflow.discovery import Discovery
from pox.lib.util import dpid_to_str
import time

'''
Pox Component to query OpenFlow-enabled switches every 10s for aggregated statistics.

'''


class portStats(EventMixin):
    def __init__(self, interval=10):
        self.portActiveCount = {}
        self.interval = interval
        core.openflow.addListeners(self)
    #Done
    def _handle_ConnectionUp(self, event):
        print "Switch %s has connected" % event.dpid
        #log.info('Switch' + dpid_to_str(event.dpid) + 'has connected')
        self.sendPortStatsRequest(event)

    def _handle_PortStatsReceived(self, event):
        sw = 's%s' % event.dpid
        self.portActiveCount[sw] = event.stats
        print "PortStatsReceived"
        for i in range(1, len(self.portActiveCount[sw])):
            print sw, " port:", self.portActiveCount[sw][i].port_no, " Total Packets Received:", self.portActiveCount[sw][i].rx_packets
            print sw, " port:", self.portActiveCount[sw][i].port_no, " Total Packets Transmitted:", self.portActiveCount[sw][i].tx_packets
            print sw, " port:", self.portActiveCount[sw][i].port_no, " Total Bytes Received:", self.portActiveCount[sw][i].rx_bytes
            print sw, " port:", self.portActiveCount[sw][i].port_no, " Total Bytes Transmitted:", self.portActiveCount[sw][i].tx_bytes


        Timer(self.interval, self.sendPortStatsRequest, args=[event])

    def sendPortStatsRequest(self, event):
        sr = of.ofp_stats_request()
        sr.type = of.OFPST_PORT
        sr.body = of.ofp_port_stats_request()
        sr.body.port_no = of.OFPP_NONE

        event.connection.send(sr)
        print "Sending port stat request message to Switch %s " % event.dpid


def launch(interval='10'):
    interval = int(interval)
    core.registerNew(portStats, interval)


