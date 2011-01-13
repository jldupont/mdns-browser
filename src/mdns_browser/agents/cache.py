"""
    Cache Agent

    MESSAGES IN:
    - "raw_service"
    - "raw_address"
    - "services?"
    
    MESSAGES OUT:
    - "service"         (service_name, server_name, server_port, addresses)
    - "service_expired" (service_name, server_name, server_port)

        
    Created on 2011-01-07
    @author: jldupont
"""
ENTRY_TIMEOUT    = 3   ##minutes

from mdns_browser.system.base import AgentThreadedBase

class CacheAgent(AgentThreadedBase):

    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.services={}
        self.addresses={}
        self.newEntry=False
        self.justAnnounced=[]

    def h___tick__(self, _ticks_per_second, 
               second_marker, min_marker, hour_marker, day_marker,
               sec_count, min_count, hour_count, day_count):
        if min_marker:
            self.justAnnounced=[]
            self._processExpired()
            
        if second_marker and self.newEntry:
            self._announceServices()
    
    def h_raw_service(self, service_name, server_name, server_port):
        self.services[service_name] = {"server_name": server_name,
                                       "server_port": server_port,
                                       "ttl":  ENTRY_TIMEOUT
                                       }
        self.newEntry=True
    
    def h_raw_address(self, server_name, address_type, address):
        try:
            self.addresses[server_name].update({address_type : address,
                                           "ttl": ENTRY_TIMEOUT})
        except:
            self.addresses[server_name]= {address_type : address,
                                           "ttl": ENTRY_TIMEOUT}
            
        self.newEntry=True

    ## ------------------------------------------------------------------
    
    def _processExpired(self):
        """ Garbage Collection
        """
        to_delete=[]
        for service_name, entry in self.services.iteritems():
            ttl = max(entry["ttl"]-1, 0)
            if ttl == 0:
                to_delete.append(service_name)
            else:
                self.services[service_name].update({"ttl": ttl})
        for service_name in to_delete:
            ##print "!! deleting: %s" % service_name
            entry = self.services[service_name]
            server_name=entry["server_name"]
            server_port=entry["server_port"]
            self.pub("service_expired", service_name, server_name, server_port)
            del self.services[service_name]
        
        to_delete=[]
        for server_name, entry in self.addresses.iteritems():
            ttl = max(entry["ttl"]-1, 0)
            if ttl==0:
                to_delete.append(server_name)
            else:
                self.addresses[server_name].update({"ttl": ttl})
            
        for server_name in to_delete:
            ##print "!! deleting: %s" % server_name
            del self.addresses[server_name]

    
    def hq_services(self):
        self._announceServices(True)
    
    def _announceServices(self, force=False):
        """ Announce all entries
        """
        self.newEntry=False
        for service_name, entry in self.services.iteritems():
            server_name=entry["server_name"]
            server_port=entry["server_port"]
            addresses=self.addresses.get(server_name, None)
            if addresses is not None:
                if service_name not in self.justAnnounced or force:
                    #print "announcing (%s): %s" % (force, service_name)
                    self.pub("service", service_name, server_name, server_port, addresses)
                    self.justAnnounced.append(service_name)
        


_=CacheAgent()
_.start()

