"""
    Comms Agent
    
    MESSAGES PROCESSED:
    - "__tick__"
    - "query"
    
    MESSAGES EMITTED:
    - "packet"
    
    
    @date: 2011-01-07
    @author: jldupont
"""
_MDNS_ADDR = '224.0.0.251'
_MDNS_PORT = 5353;
_MAX_MSG_ABSOLUTE = 8972

_SELECT_TIMEOUT=0.5

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
            a
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
        
    def h_query(self, protocol_msg):
        try:
            _bytes_sent = self.socket.sendto(protocol_msg, 0, (_MDNS_ADDR, _MDNS_PORT))
        except:
            # Ignore this, it may be a temporary loss of network connection
            pass
        
        
    def h___tick__(self, *_):
        """ Might have to tweak receive interval...
        """
        if len(self._failures) > 0:
            self.log("c", "Network Socket Error: %s" % self._failures)
        
        try:
            rr, _wr, _er = select.select([self.socket,], [], [], _SELECT_TIMEOUT)
            if rr:
                try:
                    data, (addr, port) = self.socket.recvfrom(_MAX_MSG_ABSOLUTE)
                    self.pub("packet", data, addr, port)
                except:
                    pass
        except Exception, e:
            self.pub("llog", "Receive Error: " % e)

        
        
_=CommsAgent()
_.start()
