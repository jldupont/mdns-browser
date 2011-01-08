"""
    Comms Agent
    
    Created on 2011-01-07

    @author: jldupont
"""
_MDNS_ADDR = '224.0.0.251'
_MDNS_PORT = 5353;
_DNS_PORT = 53;
_DNS_TTL = 60 * 60; # one hour default TTL
_MAX_MSG_ABSOLUTE = 8972

_SELECT_TIMEOUT=1

import socket
import select
from mdns_browser.system.base import AgentThreadedBase

class CommsAgent(AgentThreadedBase):
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self._failures=[]
        
        ## can't really fail here
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            ##The following doesn't work on Linux
            try:    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            except: pass
        except:
            self._failures.append("Socket Options: REUSEADDR")
        
        try:    
            self.socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 255)
            self.socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        except:
            self._failures.append("Socket Options: Multicast")

        try:
            self.group = ('', _MDNS_PORT)
            self.socket.bind(self.group)
        except:
            # Some versions of linux raise an exception even though
            # the SO_REUSE* options have been set, so ignore it
            #
            pass
        self.socket.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF,   socket.inet_aton('0.0.0.0'))
        self.socket.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(_MDNS_ADDR) + socket.inet_aton('0.0.0.0'))
        
    def h___tick__(self, *_):
        try:
            rr, _wr, _er = select.select([self.socket,], [], [], _SELECT_TIMEOUT)
            if rr:
                try:
                    data, (addr, port) = self.socket.recvfrom(_MAX_MSG_ABSOLUTE)
                    self.pub("packet", data, addr, port)
                except Exception,e:
                    # Ignore errors that occur on shutdown
                    print e
        except Exception,e:
            print "CommsAgent: %s" %e

        
        
_=CommsAgent()
_.start()
