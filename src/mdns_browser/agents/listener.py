"""
    Listener Agent

    Listens for "DNS Answers" and issues "Answer" message
    
    Created on 2011-01-07
    @author: jldupont
"""
from mdns_browser.system.base import AgentThreadedBase
from mdns_browser.mdns import DNSIncoming, DNSService

class ListenerAgent(AgentThreadedBase):
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

    def h_packet(self, packet_data, addr, port):
        try:
            protocol_msg=DNSIncoming(packet_data)
            if protocol_msg.isResponse():
                self._handleMsg(protocol_msg)
        except:
            pass
    
    def _handleMsg(self, msg):
        for answer in msg.answers:
            if type(answer) is DNSService:
                print "service: port: %s, server: %s" % (answer.port, answer.server)
                self.pub("service", answer)
            

_=ListenerAgent()
_.start()
