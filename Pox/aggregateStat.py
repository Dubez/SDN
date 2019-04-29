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


class aggregateStats(EventMixin):
    def __init__(self, interval=10):
        self.aggregateActiveCount = {}
        self.interval = interval
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self, event):
        print "Switch %s has connected" % event.dpid
        self.sendAggregateStatsRequest(event)

    def _handle_AggregateFlowStatsReceived(self, event):
        sw = 's%s' % event.dpid
        self.aggregateActiveCount[sw] = event.stats
        print "AggregateStatsReceived"

        print sw, " Total Packet Count:", self.aggregateActiveCount[sw].packet_count
        print sw, " Total Byte Count:", self.aggregateActiveCount[sw].byte_count
        print sw, " Total Flow Count:", self.aggregateActiveCount[sw].flow_count

        Timer(self.interval, self.sendAggregateStatsRequest, args=[event])

    def sendAggregateStatsRequest(self, event):
        sr = of.ofp_stats_request()
        sr.type = of.OFPST_AGGREGATE
        sr.body = of.ofp_aggregate_stats_request()
        event.connection.send(sr)
        print "Sending aggregate stat request message to Switch %s " % event.dpid


def launch(interval='10'):
    interval = int(interval)
    core.registerNew(aggregateStats, interval)
