'''
Created on 2011-01-07

@author: jldupont
'''

from mdns_browser.system.base import AgentThreadedBase

class DebugAgent(AgentThreadedBase):
    def __init__(self):
        AgentThreadedBase.__init__(self)
        
    def h_log(self, level, msg, *pargs):
        if level!="d":
            return
        
        try:
            str = msg % pargs
            print "DEBUG: %s" % str
        except:
            print "DEBUG: %s" % msg
        
        
    #def h_packet(self, data, addr, port):
    #    print "* packet: (%s, %s)" % (addr, port)

    #def h_service(self, *pargs):
    #    print "DEBUG -- SERVICE: %s, %s, %s, %s" % pargs 

_=DebugAgent()
_.start()

