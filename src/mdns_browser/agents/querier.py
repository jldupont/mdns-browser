"""
    Querier Agent

    Issues the query for the _http._tcp services periodically
    
    Created on 2011-01-07
    @author: jldupont
"""
QUERY_TIMEOUT = 1 ##minutes
SERVICE_TO_BROWSE_FOR="_http._tcp.local."

from mdns_browser.system.base import AgentThreadedBase
from mdns_browser.mdns import DNSOutgoing, DNSQuestion, _FLAGS_QR_QUERY, _TYPE_PTR, _CLASS_IN

class QuerierAgent(AgentThreadedBase):
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self._generate()

    def h___tick__(self, _ticks_per_second, 
               second_marker, min_marker, hour_marker, day_marker,
               sec_count, min_count, hour_count, day_count):
        if min_marker:
            self._generate()
    
    def _generate(self):
        out = DNSOutgoing(_FLAGS_QR_QUERY)
        out.addQuestion(DNSQuestion(SERVICE_TO_BROWSE_FOR, _TYPE_PTR, _CLASS_IN))
        self.pub("query", out.packet())
            

_=QuerierAgent()
_.start()
