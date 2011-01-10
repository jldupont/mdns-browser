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
        if status=="started":
            self.num_agents_started += 1
            return
        
        if status=="halted":
            self.num_agents_halted += 1
        
        if self.num_agents_started == self.num_agents_halted:
            self._pub("__quit__")
        
    def h___log__(self, logLevel, _msg, *pargs):

        if logLevel == "c" or logLevel=="C":
            self._pub("__halt__")
            

_=SupervisorAgent()
_.start()
