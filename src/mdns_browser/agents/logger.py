"""
    Logger Agent
    
    Created on 2011-01-07

    @author: jldupont
"""

from mdns_browser.system.base import AgentThreadedBase

class LoggerAgent(AgentThreadedBase):
    
    MAP = {"d": "DEBUG",
           "i": "INFO",
           "w": "WARNING",
           "e": "ERROR",
           "c": "CRITICAL"
           }
    
    def __init__(self):
        AgentThreadedBase.__init__(self)
        
    def h___tick__(self, _ticks_per_second, 
                   second_marker, min_marker, hour_marker, day_marker,
                   sec_count, min_count, hour_count, day_count):
        """ 
        Timebase used to replenish credits: 1 min
        """
        if min_marker:
            self.pub("logcredits", {"w": 2, "e": 2, "i": 20})

    def h___log__(self, logLevel, msg, *pargs):
        self.h_log(logLevel, msg, *pargs)
        
    def h_log(self, logLevel, msg, *pargs):
        tag=self.MAP.get(logLevel, "INFO")
        try:
            str = msg % pargs
            print "%s: %s" % (tag, str)
        except:
            print "%s: %s" % (tag, msg)
        

_=LoggerAgent()
_.start()
