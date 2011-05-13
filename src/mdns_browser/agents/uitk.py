"""
Created on 2011-01-12

@author: jldupont
"""
from Tkinter import *
import webbrowser

import mdns_browser.system.mswitch as mswitch
from mdns_browser.system.base import Agent

TIME_BASE=250
TICKS_SECOND=1000/TIME_BASE


class UiWindow(Frame): #@UndefinedVariable
    """
        Service Name ,  Server Name , Server Address , Server Port
    
    """
    def __init__(self, opts):
        Frame.__init__(self, None)

        self.opts=opts
        self.ag=Agent(self, TICKS_SECOND)
        
        self.master.config(width=100)
        
        self.lb=Listbox(self.master)
        self.lb.pack(fill=BOTH, expand=True)
        
        self.bquit=Button(self.master, text="Quit", command=self.quit)
        self.bquit.pack()
        
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        
        self.list_services={}
        
        self.after(TIME_BASE, self.__tick)
        
    def quit(self):
        self.do_destroy()
        self.master.destroy()
        
    def do_destroy(self, *_):
        mswitch.publish(self, "__quit__")
        
    def __tick(self, *_):
        """
        Clock 'tick'
        """
        if self.ag.pump():
            self.quit()

        self.after(TIME_BASE, self.__tick)
                    
    ## =========================================================================================
    ##
    ##  MESSAGE HANDLERS
    ##
    def h_service(self, service_name, server_name, server_port, addresses):
        """
        When a Service is added
        """
        self.lb.insert(END, "%s:%s:%s" % (service_name, server_name, server_port))
            
    def h_service_expired(self, service_name, server_name, server_port):
        """
        When a Service turns expired
        """
    
    ## =========================================================================================
        
        
    def add_service(self, service_name, server_name, server_port, addresses):
        
        entry=self.list_services.get((service_name, server_name), None)
        if entry is not None:
            return
        
        #print "!! Ui Window: adding service: %s" % service_name 
        if self._filtered(service_name):
            self.list_services[(service_name, server_name)]={
                                            "server_name": server_name, 
                                            "ipv4":  addresses["ipv4"], 
                                            "port":  server_port
                                            }
        
    def remove_service(self, service_name, server_name, server_port):
        #print "!! Ui Window: removing: %s " % service_name
        try:
            del self.list_services[(service_name, server_name)]
        except:
            pass


    def row_activated(self, tv, path, *_):
        entry=self.list_services[path]
        _service_name, _server_name, address, port=entry
        #print ">> selected: %s" % service_name
        url="http://%s:%s/" % (address, port)
        webbrowser.open(url, new=0, autoraise=True)

    def _filtered(self, service_name):
        filters=self.opts["service_filters"]
        if len(filters)==0:
            return True
        for filter in filters:
            #print "* trying filter: "+filter
            if service_name.startswith(filter.strip()):
                return True
        return False


        
        
if __name__=="__main__":
    ui=UiWindow()
    ui.mainloop()
    print "end!"
    mswitch.quit()
    sys.exit()
