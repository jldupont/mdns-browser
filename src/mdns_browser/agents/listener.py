"""
    Listener Agent

    Listens for "DNS Answers" and issues "Answer" message
    
    Created on 2011-01-07
    @author: jldupont
"""
import socket

from mdns_browser.system.base import AgentThreadedBase
from mdns_browser.mdns import DNSIncoming, DNSService, DNSAddress

class ListenerAgent(AgentThreadedBase):
    
    def __init__(self):
        AgentThreadedBase.__init__(self)

    def h_packet(self, packet_data, addr, port):
        try:
            protocol_msg=DNSIncoming(packet_data)
            if protocol_msg.isResponse():
                self._handleMsg(protocol_msg)
        except Exception, e:
            print e
    
    def _handleMsg(self, msg):
        for answer in msg.answers:
            if type(answer) is DNSService:
                print "service: port: %s, server: %s" % (answer.port, answer.server)
                self.pub("service", answer)
            if type(answer) is DNSAddress:
                address_type="ipv4" if answer.type==1 else "ipv6"
                try:
                    address= socket.inet_ntoa(answer.address)
                except:
                    address=answer.address
                print "address: name: %s, %s, %s" % (str(answer.name), address_type, address)
                self.pub("address", str(answer.name), address_type, address)
            

_=ListenerAgent()
_.start()
