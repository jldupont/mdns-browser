"""
    Base class for threaded Agents
    
    * high/low priority message queues
    * message bursting controlled
    * message dispatching based on Agent 'interest'
    * default handler: "h_default" , catch-all messages
    * "snooping" handlers support: agent gets "envelopes" with only 'msgType'
    * logging support: credit based, throttling at the 'source'
    
    
    NOTES:
    - The logLevel "d" (debug) is un-throttled: beware!
    
    @author: jldupont
    @date: May 17, 2010
    @revised: June 18, 2010
    @revised: August 22, 2010 :  filtered-out "send to self" case
    @revised: August 23, 2010 :  added "snooping mode", remove another message loop, tidied-up
    @revised: January 10, 2011:  added 'logging' facility helper  
"""

from threading import Thread
from Queue import Queue, Empty
import uuid

import mswitch

__all__=["AgentThreadedBase", "AgentThreadedWithEvents", "debug", "debug_interest" 
         "mdispatch", 
         "process_queues", "message_processor"]

debug=False
debug_interest=False


def mdispatch(obj, this_source, envelope):
    """
    Dispatches a message to the target
    handler inside a class instance
    
    @return (__quit__, mtype, handled, snooping)
    
    handled:  None  --> rejected because sending to self
    handled:  True  --> message was handled by agent
    handled:  False --> message wasn't handled by agent -- no interest
    """
    orig, mtype, payload = envelope
    
    ## on snooping handlers...
    try:    pargs, kargs = payload
    except: 
        pargs=()
        kargs=()
    
    ## Avoid sending to self -- shouldn't occur at this point anyways
    if orig == this_source:
        print "************* mdispatch: dropped: orig(%s) obj_orig(%s) mtype(%s)" % (orig, this_source, mtype)
        return (False, mtype, None, False)

    if mtype=="__quit__":
        return (True, mtype, None, False)

    handled=False
    snoopingHandler=False

    if mtype.endswith("?"):
        handlerName="hq_%s" % mtype[:-1]
        sHandlerName="hqs_%s" % mtype[:-1]
    else:
        handlerName="h_%s" % mtype
        sHandlerName="hs_%s" % mtype
        
    handler =getattr(obj, handlerName, None)
    shandler=getattr(obj, sHandlerName, None)    
    
    if handler is None:
        if shandler is not None:
            snoopingHandler=True
            handler=shandler
    
    if handler is None:
        handler=getattr(obj, "h_default", None)    
        if handler is not None:
            handler(mtype,*pargs, **kargs)
            handled=True
    else:
        handled=True
        if snoopingHandler:
            handler()
        else:
            handler(*pargs, **kargs)

    return (False, mtype, handled, snoopingHandler)


def process_queues(halting, src_agent, agent_name, agent_id, interest_map, responsesInterestList,
                   iq, isq, processor, low_priority_burst_size=5):
    """
    Runs through both queues and calls processing on valid messages
    """
    ## HIGH PRIORITY QUEUE
    quit=False
    while True:
        try:
            envelope=isq.get(block=True, timeout=0.1)
            quit=processor(src_agent, agent_name, agent_id, interest_map, responsesInterestList, iq, isq, envelope)
            if quit:
                quit=True
                break
        except Empty:
            break

    ## LOW PRIORITY QUEUE
    ##  process only if the system is not shutting down        
    if not halting:
        burst=low_priority_burst_size
        while True and not quit:                
            try:
                envelope=iq.get(block=False)#(block=True, timeout=0.1)
                processor(src_agent, agent_name, agent_id, interest_map, responsesInterestList, iq, isq, envelope)
                burst -= 1
                if burst == 0:
                    break
            except Empty:
                break
    
    return quit
    
def message_processor(src_agent, agent_name, agent_id, interest_map, responsesInterestList, iq, isq, envelope):
    """
    Processes 1 message envelope
    
    Used in conjunction with 'process_queues'
    """
    orig, mtype, _payload = envelope
    
    interested=interest_map.get(mtype, None)
    if interested==False:
        return False
    
    quit, _mtype, handled, snooping=mdispatch(src_agent, agent_id, envelope)
    if quit:
        shutdown_handler=getattr(src_agent, "h_shutdown", None)
        if shutdown_handler is not None:
            shutdown_handler()
        return True

    ## not much more to do here...
    ## but shouldn't happen anyhow!!! #paranoia...
    if handled is None:
        return

    if interested is None:
        if mtype!="__quit__":
            if mtype not in responsesInterestList:
                mswitch.publish(agent_id, "__interest__", agent_name, agent_id, mtype, handled, snooping, iq, isq)
                responsesInterestList.append(mtype)

                ## stop sending to self definitely
                if handled is None:
                    handled=False
                    
                if debug_interest:
                    print "+++ interest msg-orig(%s) target(%s) mtype(%s): (%s)" % (orig, agent_name, mtype, handled)
                interest_map[mtype]=handled
        
    return quit

class AgentThreadedBase(Thread):
    """
    Base class for Agent running in a 'thread' 
    """
    
    LOW_PRIORITY_BURST_SIZE=5
    
    HP_LOGGING = ["c", "e"]
    
    def __init__(self, debug=False):
        Thread.__init__(self)
        self.mmap={}
        
        self.debug=debug
        self.id = uuid.uuid1()
        self.iq = Queue()
        self.isq= Queue()
        
        self.agent_name=str(self.__class__).split(".")[-1][:-2]
        self.responsesInterest=[]
        self.credits={}
        self.logstats={}
        self.halting=False
        self.quit=False
        
    def dprint(self, msg):
        """ Simple debugging facility
        """
        if debug:
            print "+ %s: %s" % (self.agent_name, msg)
        
    def pub(self, msgType, *pargs, **kargs):
        """ Message Publication facility
        """
        if not self.halting:
            mswitch.publish(self.id, msgType, *pargs, **kargs)

    def _pub(self, msgType, *pargs, **kargs):
        """ Message Publication facility
        """
        mswitch.publish(self.id, msgType, *pargs, **kargs)
        
        
    def h___halt__(self):
        """ System is preparing to shutdown
        """
        self.halting=True
        self._pub("__agent__", self.agent_name, self.id, "halted")
        print "* Agent(%s) (%s) HALTED" % (self.agent_name, self.id)
        
    def h_logcredits(self, credits):
        """ Reception of logging credits
        
            ** Don't add credits to existing ones **
        """
        try:    self.credits.update(credits)
        except: pass
        self._pub("__logstats__", self.agent_name, self.id, self.logstats)
        
    def log(self, logLevel, *pargs):
        """ Logging Facility
            
            Throttles messages at the source
            
            For starters, every logLevel gets 1 credit 
        """
        if self.credits.get(logLevel, 1) == 0:
            self.logstats[logLevel] = self.logstats.get(logLevel, 0)+1
            return
    
        if logLevel in self.HP_LOGGING:
            self._pub("__log__", logLevel, *pargs)
        else:
            self._pub("log", logLevel, *pargs)
            
        if logLevel != "d" and logLevel != "D":
            self.credits[logLevel]=self.credits.get(logLevel, 1)-1
        
    def beforeRun(self):
        pass
        
    def doQuit(self):
        self.quit=True
        
    def run(self):
        """
        Main Loop
        """
        ## subscribe this agent to all
        ## the messages of the switch.
        ## Later on when the agent starts receiving messages,
        ## it will signal which 'message types' are of interest.
        mswitch.subscribe(self.id, self.iq, self.isq)
        
        getattr(self, "beforeRun")()
        
        print "Agent(%s) (%s) starting" % (self.agent_name, self.id)
        self._pub("__agent__", self.agent_name, self.id, "started")
        
        quit=False
        while not self.quit and not quit:
            quit=process_queues(self.halting, self, self.agent_name, self.id, 
                                self.mmap, self.responsesInterest,
                                self.iq, self.isq, message_processor)
        
        ##self._pub("__agent__", self.agent_name, self.id, "stop")    
        print "Agent(%s) (%s) ending" % (self.agent_name, self.id)
                
            

class AgentThreadedWithEvents(AgentThreadedBase):
    """
    A base class for threaded Agents with timer based events support
    
    @param timers_spec: dictionary where each key represents a timer entry
    
    Timer Entry:
    ============
        [seconds_timeout, minutes_timeout, hours_timeout, days_timeout]
        
        E.g.
        ("sec", 2, callback) : will fire "callback" every 2 seconds
        ("min", 5, callback) : will fire "callback" every 5 minutes
    """
    def __init__(self, timers_spec=[], debug=False):
        AgentThreadedBase.__init__(self, debug)
        
        try:    ts=self.__class__.TIMERS_SPEC
        except: ts=[]
        
        self.timers_spec=timers_spec or ts
        self._timers={"sec":[], "min": [], "hour":[], "day": []}

        try:        
            self._processTimersSpec()
        except:
            raise RuntimeError("timers_spec misconfigured for Agent: %s" % self.__class__)
        
    def _processTimersSpec(self):
        """
        Process the timers_spec required for the Agent
        """
        for timer in self.timers_spec:
            base, interval, callback_name=timer
            entries=self._timers.get(base, [])
            entries.append((interval, callback_name))
        
        
    def h___tick__(self, _ticks_per_second, 
               second_marker, min_marker, hour_marker, day_marker,
               sec_count, min_count, hour_count, day_count):
        """
        CRON like support
        """
        #print "%s: __tick__" % (self.__class__,)
        #print "h_tick: sec_count(%s) min_count(%s) hour_count(%s) day_count(%s)" % (sec_count, min_count, hour_count, day_count)
        #print "h_tick: sec(%s) min(%s) hour(%s) day(%s)" % (second_marker, min_marker, hour_marker, day_marker)
        if second_marker:
            self._processTimers(sec_count, "sec")
        if min_marker:
            self._processTimers(min_count, "min")
        if hour_marker:
            self._processTimers(hour_count, "hour")
        if day_marker:
            self._processTimers(day_count, "day")
        
    def _processTimers(self, count, base):
        for entry in self._timers[base]:
            interval, callback_name = entry
            if (count % interval==0):
                callback=getattr(self, callback_name)
                callback(base, count)
                

                


class TickGenerator(object):
    """
    Time base generator
    
    Issues a 'tick' message through a 'publisher' with parameters:
    
    'tick_second', 'tick_min', 'tick_hour' and 'tick_day'
    whilst maintaining a count for each intervals
    """
    def __init__(self, ticks_second, publisher):
        self.ticks_second=ticks_second
        self.publisher=publisher

        self.tick_count=0
        self.sec_count=0
        self.min_count=0
        self.hour_count=0
        self.day_count=0
        
    def input(self):
        """
        Performs 'tick' dispatching
        """
        tick_min=False
        tick_hour=False
        tick_day=False
        tick_second = (self.tick_count % self.ticks_second) == 0 
        self.tick_count += 1
        
        if tick_second:
            self.sec_count += 1

            tick_min=(self.sec_count % 60)==0
            if tick_min:
                self.min_count += 1
                
                tick_hour=(self.min_count % 60)==0
                if tick_hour:
                    self.hour_count += 1
                    
                    tick_day=(self.hour_count % 24)==0
                    if tick_day:
                        self.day_count += 1
        
        #print "tick! ", tick_second
        self.publisher(self.ticks_second, 
                        tick_second, tick_min, tick_hour, tick_day, 
                        self.sec_count, self.min_count, self.hour_count, self.day_count)
        
        ## just in case this is used along with gobject...
        return True
    
    
def custom_dispatch(source, q, pq, dispatcher, low_priority_burst_size=5):
    """
    For customer dispatching
    
    @param source: identifier for 'source'
    @param low_priority_burst_size: integer, maximum size of normal queue processing at a time 
    @param q: normal queue
    @param pq: priority queue
    @param dispatcher: callable
    """
    while True:
        try:     
            envelope=pq.get(False)
            orig, mtype, payload = envelope
            pargs, _kargs = payload
            
            ## skip self
            if orig==source:
                continue
            handled, snooping=dispatcher(mtype, *pargs)
            if handled==False:
                ## low overhead - once per run
                print "* '%s': not interest in '%s' message type" % (orig, mtype)
                mswitch.publish(source, "__interest__", source, mtype, False, snooping, q, pq)
                break
        except Empty:
            break
        continue            
    
    burst=low_priority_burst_size
    
    while True:
        try:     
            envelope=q.get(False)
            orig, mtype, payload = envelope
            pargs, _kargs = payload

            ## skip self
            if orig==source:
                continue
            handled, snooping=dispatcher(mtype, *pargs)
            if handled==False:
                ## low overhead - once per run
                print "* '%s': not interest in '%s' message type" % (orig, mtype)
                mswitch.publish(source, "__interest__", source, mtype, False, snooping, q, pq)
            burst -= 1
            if burst == 0:
                break
        except Empty:
            break
        
        continue
    

def dispatcher(source, q, pq, low_priority_burst_size=5):
    """
    Message dispatcher
    """
    while True:
        try:     
            envelope=pq.get(False)
            orig, mtype, payload = envelope
            pargs, _kargs = payload
            
            ## skip self
            if orig==source:
                continue
            handled, snooping=dispatcher(mtype, *pargs)
            if handled==False:
                ## low overhead - once per run
                print "* '%s': not interest in '%s' message type" % (orig, mtype)
                mswitch.publish(source, "__interest__", source, mtype, False, snooping, pq)
                break
        except Empty:
            break
        continue            
    
    burst=low_priority_burst_size
    
    while True:
        try:     
            envelope=q.get(False)
            orig, mtype, payload = envelope
            pargs, _kargs = payload

            ## skip self
            if orig==source:
                continue
            handled, snooping=dispatcher(mtype, *pargs)
            if handled==False:
                ## low overhead - once per run
                print "* '%s': not interest in '%s' message type" % (orig, mtype)
                mswitch.publish(source, "__interest__", source, mtype, False, snooping, q)
            burst -= 1
            if burst == 0:
                break
        except Empty:
            break
        
        continue
    
