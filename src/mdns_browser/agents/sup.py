"""
    Supervisor Agent

    - Keeps track of the # of Agents running
    - Initiates "halt" when a "critical" event occurs
    - Sends "__quit__" signal when all Agents are "halted"
    
    Created on 2011-01-07
    @author: jldupont
"""

from mdns_browser.system.base import AgentThreadedBase

class SupervisorAgent(AgentThreadedBase):
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        self.num_agents_started=0
        self.num_agents_halted=0
    
    def h___agent__(self, name, id, status):
        ##print "SUP.h___agent__: %s, %s, %s" % (name, id, status)
        if status=="started":
            self.num_agents_started += 1
            return
        
        if status=="halted":
            self.num_agents_halted += 1
        
        if self.num_agents_started == self.num_agents_halted:
            self._pub("__quit__")
            self.doQuit()

    def h_log(self, logLevel, *pargs):

        if logLevel == "c" or logLevel=="C":
            self._pub("__halt__")
        
    def h___log__(self, logLevel, *pargs):
        if logLevel == "c" or logLevel=="C":
            self._pub("__halt__")
            

_=SupervisorAgent()
_.start()
