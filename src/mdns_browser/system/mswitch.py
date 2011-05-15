"""
    Message Switch
    
    * high/low priority queues
    * message dispatching based on 'interest' communicated by Agent
    * message bursting controlled
    
    @author: jldupont
    @date: May 17, 2010
    @revised: June 18, 2010
    @revised: August 22, 2010 :  filtered-out "send to self" case 
    @revised: August 23, 2010 :  added "snooping mode"   
    @revised: January 10, 2011:  added "halting" operational mode
    @revided: May 15, 2011    :  added better winding-down support 
"""

from threading import Thread
from Queue import Queue, Empty

__all__=["publish", "subscribe", "quit", "observe_mode"]
OBSERVE_FILTER_OUT=["__tick__", "log", "llog"]
OBSERVE_FILTER_OUT_SOURCES=["__bridge__",]
#OSBSERVE_FILTER_OUT=["log", "llog"]
            
observe_mode=False
debugging_mode=False

class CentralSwitch(Thread):
    """
    Simple message switch
    
    Really just broadcasts the received
    message to all 'clients' in 'split horizon'
    i.e. not sending back to originator
    """
    
    LOW_PRIORITY_BURST_SIZE=5
    
    def __init__(self):
        Thread.__init__(self)
        
        self.quitting=False
        self.halting=False
        #self.rmap={} ## debug only
        
        self.imap={}
        self.clients=[]
        self.iq=Queue()
        
        ## system queue - high priority
        self.isq=Queue()
        
        ## Agent tracking
        self.agent_count=0
        self.agent_halted_count=0
    
    def run(self):
        """
        Main loop
        
        Process the messages in the input queues of the switch.
        Each message is inspected and dispatched appropriately 
        to the client subscribers.
        
        The system messages "__interest__" and "__quit__" are
        given special attention.
        
        Be sure to pass along the "__quit__" message **before**
        the switch thread.
        """
        quit=False
        while not quit:
            while True:
                
                ### There should be only a low volume/frequency
                ### of 'high priority' system messages.
                ### We'll get back through here soon enough i.e.
                ###  after the other queue's timeout / 1 msg processed
                try:
                    envelope=self.isq.get(block=False)
                    orig, mtype, payload=envelope

                    if mtype != "__tick__" and debugging_mode:
                        print "mswitch: mtype(%s)" % mtype
                    
                    if mtype=="__interest__":
                        self.do_interest(payload)
                        continue

                    self.do_pub(orig, mtype, payload)
                    
                    if mtype=="__agent__":
                        self.agent_count = self.agent_count + 1
                        
                    if mtype=="__halted__":
                        self.agent_halted_count = self.agent_halted_count + 1
                        if self.agent_count==self.agent_halted_count:
                            quit=True
                    
                    ## We needed to give a chance to
                    ## all threads to exit before
                    ## committing "hara-kiri"
                    if mtype=="__quit__":
                        self.quitting=True
                        break

                    if mtype=="__halt__":
                        self.halting=True
                        continue
                    
                except Empty:
                    break
    
            burst=self.LOW_PRIORITY_BURST_SIZE
            
            while not self.halting and not quit:
                try:            
                    ## normal priority queue            
                    envelope=self.iq.get(block=True, timeout=0.1)
                    orig, mtype, payload=envelope
                    if mtype=="__sub__":
                        q, sq=payload
                        self.do_sub(orig, q, sq)
                    else:
                        self.do_pub(orig, mtype, payload)

                    if mtype != "__tick__" and debugging_mode:
                        print "mswitch: mtype(%s)" % mtype
                    
                    ## Only processed a "burst" of low priority messages
                    ##  before checking the "high priority" queue
                    burst -= 1
                    if burst==0:
                        break
                except Empty:
                    break
        
        #print "* mswitch: ending"
        
    def do_interest(self, args):
        """
        Add a 'subscriber' for 'mtype' to the "interested" list
        """
        payload, _kargs = args
        agent_name, agent_id, mtype, interest, snooping, _q, _iq = payload
        self.imap[(agent_id, mtype)]=(interest, snooping)
        
        if debugging_mode:
            print ":::: do_interest: source(%s) mtype(%s) interest(%s) snooping(%s)" % (agent_name, mtype, interest, snooping)
               
                
    def do_sub(self, orig, q, sq):
        """
        Performs subscription
        """
        self.clients.append((orig, q, sq))
        
    def do_pub(self, orig, mtype, payload):
        """
        Performs message distribution
        """
        #print "do_pub: mtype: %s  payload: %s" % (mtype, payload)
        for sorig, q, sq in self.clients:
            
            ## don't send to self!
            if sorig==orig:
                continue
            
            (interest,  snooping)=self.imap.get((sorig, mtype), (None, None))
            
            if observe_mode:
                if mtype not in OBSERVE_FILTER_OUT:
                    if orig not in OBSERVE_FILTER_OUT_SOURCES:
                        if interest:
                            print "<<< do_pub: orig(%s) interest(%s) mtype(%s) q(%s) sq(%s)" % (orig, interest, mtype, q, sq)
                
            ### Agent notified interest OR not sure yet            
            if interest==True or interest==None:

                if mtype.startswith("__"):
                    if snooping:
                        sq.put((orig, mtype, None), block=False)
                    else:
                        sq.put((orig, mtype, payload), block=False)
                else:
                    if snooping:
                        q.put((orig, mtype, None), block=False)
                    else:
                        q.put((orig, mtype, payload), block=False)
            #if mtype!="tick":                    
            #    print ">>> do_pub: mtype(%s) q(%s) sq(%s)" % (mtype, q, sq)
    


## ===============================================================  
## =============================================================== API functions
## =============================================================== 
        

def publish(orig, msgType, *pargs, **kargs):
    """
    Publish a 'message' of type 'msgType' to
    all registered 'clients'
    """
    if msgType.startswith("__"):
        _switch.isq.put((orig, msgType, (pargs, kargs)), block=False)
    else:
        _switch.iq.put((orig, msgType, (pargs, kargs)), block=False)
    
    
def subscribe(orig, q, sq, _msgType=None):
    """
    Subscribe a 'client' to all the switch messages
     
    @param q: client's input queue
    """
    _switch.iq.put((orig, "__sub__", (q, sq)))
    

def quit(orig="__main__"):
    _switch.isq.put((orig, "__quit__", ([], {})), block=False)


_switch=CentralSwitch()
_switch.start()
