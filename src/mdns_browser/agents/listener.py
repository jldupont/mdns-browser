"""
    Listener Agent

    Listens for "DNS Answers" and issues "Service" & "Address" messages
    
    MESSAGES OUT:
    - "service"
    - "address"
    
    MESSAGES IN:
    - "packet"
    
    
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
                #self.log("i", "service: name: %s, port: %s, server: %s" % (answer.name, answer.port, answer.server))
                self.pub("service", answer.name, answer.server, answer.port)
            if type(answer) is DNSAddress:
                address_type="ipv4" if answer.type==1 else "ipv6"
                try:
                    address= socket.inet_ntoa(answer.address)
                except:
                    address=answer.address
                #self.log("i", "address: name: %s, %s, %s, %s" % (str(answer.name), address_type, address, answer.ttl))
                self.pub("address", str(answer.name), address_type, address)
            

_=ListenerAgent()
_.start()
