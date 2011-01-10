"""
    Cache Agent

        
    Created on 2011-01-07
    @author: jldupont
"""
from mdns_browser.system.base import AgentThreadedBase

class CacheAgent(AgentThreadedBase):

    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.services={}
        self.addresses={}

    def h___tick__(self, _ticks_per_second, 
               second_marker, min_marker, hour_marker, day_marker,
               sec_count, min_count, hour_count, day_count):
        if min_marker:
            self._processExpired()
    
    def h_service(self, name, server, port):
        pass
    
    def h_address(self, name, type, address):
        pass

_=CacheAgent()
_.start()
