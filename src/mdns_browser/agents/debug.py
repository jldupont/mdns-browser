'''
Created on 2011-01-07

@author: jldupont
'''

from mdns_browser.system.base import AgentThreadedBase

class DebugAgent(AgentThreadedBase):
    def __init__(self):
        AgentThreadedBase.__init__(self)
        
        
    def h_packet(self, data, addr, port):
        print "* packet: (%s, %s)" % (addr, port)


_=DebugAgent()
_.start()

