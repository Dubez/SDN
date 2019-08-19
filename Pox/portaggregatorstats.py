from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.revent import *
from pox.lib.recoco import Timer
from collections import defaultdict
from pox.openflow.discovery import Discovery
from pox.lib.util import dpid_to_str
import time
import sleep

'''
Pox Component to query OpenFlow-enabled switches every 10s for aggregated statistics.
Some log info to be trimmed.

'''


class aggregateStats(EventMixin):
    def __init__(self, interval=5):  # usually 10
        self.aggregateActiveCount = {}
        self.portActiveCount = {}
        self.interval = interval
        self.previous = 0
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        print "Switch %s has connected" % event.dpid
        sleep.switch_table.add_switch(sleep.switch(event.dpid))
        self.sendAggregateStatsRequest(event)
        self.sendPortStatsRequest(event)

    def _handle_AggregateFlowStatsReceived(self, event):
        sw = 's%s' % event.dpid
        self.aggregateActiveCount[sw] = event.stats
        print "AggregateStatsReceived"

        self.bits = self.aggregateActiveCount[sw].byte_count

        self.since_last = self.bits - self.previous
        print sw, " Total Byte Count:", self.bits, 'and diff', self.since_last

        # add dpid, lid, linkbw to array
        sleep.print_to_file([self.since_last])

        # for each port arr += [lid,lbw] then print

        self.previous = self.bits

        Timer(self.interval, self.sendAggregateStatsRequest, args=[event])

    def _handle_PortStatsReceived(self, event):
        sww = 's%s' % event.dpid
        self.portActiveCount[sww] = event.stats
        print "PortStatsReceived"
        for i in range(1, len(self.portActiveCount[sww])):
            if self.portActiveCount[sww][i].port_no >60000:
                continue
            else:
                print sww, " port:", self.portActiveCount[sww][i].port_no, " Total Packets Received:", \
                    self.portActiveCount[sww][i].rx_packets
                print sww, " port:", self.portActiveCount[sww][i].port_no, " Total Packets Transmitted:", \
                    self.portActiveCount[sww][i].tx_packets
                print sww, " port:", self.portActiveCount[sww][i].port_no, " Total Bytes Received:", self.portActiveCount[sww][
                    i].rx_bytes
                print sww, " port:", self.portActiveCount[sww][i].port_no, " Total Bytes Transmitted:", \
                    self.portActiveCount[sww][i].tx_bytes
        Timer(self.interval, self.sendPortStatsRequest, args=[event])

    def sendAggregateStatsRequest(self, event):
        sr = of.ofp_stats_request()
        sr.type = of.OFPST_AGGREGATE
        sr.body = of.ofp_aggregate_stats_request()

        event.connection.send(sr)
        print "Sending aggregate stat request message to Switch %s " % event.dpid

    def sendPortStatsRequest(self, event):
        srr = of.ofp_stats_request()
        srr.type = of.OFPST_PORT
        srr.body = of.ofp_port_stats_request()
        srr.body.port_no = of.OFPP_NONE

        event.connection.send(srr)
        print "Sending port stat request message to Switch %s " % event.dpid


def launch(interval='2'):
    interval = int(interval)
    core.registerNew(aggregateStats, interval)
