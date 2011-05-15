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

        self.master.title("MDNS Browser")

        self.opts=opts
        self.ag=Agent(self, TICKS_SECOND)
        
        self.lb=Listbox(self.master)
        self.lb.pack(fill=BOTH, expand=True)
        self.lb.bind("<Double-Button-1>", self._dblClick)
        
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
        
    def _dblClick(self, *_):
        index=self.lb.curselection()
        entry=self.lb.get(index)
        try:
            entry=self.from_string(entry)
            print entry
            _service_name, _server_name, port, address = entry
            url="http://%s:%s/" % (address, port)
            webbrowser.open(url, new=0, autoraise=True)
        except Exception, e:
            """ Shouldn't happen but just in case...
            """
            print "ERROR: %s" % e
            
        
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
    def h_service(self, *p):
        """
        When a Service is added
        """
        self.add_service(*p)
            
    def h_service_expired(self, *p):
        """
        When a Service turns expired
        """
        self.remove_service(*p)
        self.lb.delete(0, END)
        for entry in self.list_services:
            self.lb.insert(END, *entry)
    
    ## =========================================================================================
        
        
    def add_service(self, *p):
        
        service_name, server_name, server_port, addresses = p
        
        entry=self.list_services.get((service_name, server_name), None)
        if entry is not None:
            return
        
        #print "!! Ui Window: adding service: %s" % service_name 
        if self._filtered(service_name):
            address_v4=addresses["ipv4"]
            
            self.list_services[(service_name, server_name)]={
                                            "server_name": server_name, 
                                            "ipv4":  addresses["ipv4"], 
                                            "port":  server_port
                                            }
            self.lb.insert(END, self.to_string(service_name, server_name, server_port, address_v4))
        else:
            print "INFO: filtered out: %s" % service_name
            
        
    def remove_service(self, service_name, server_name, server_port):
        #print "!! Ui Window: removing: %s " % service_name
        try:
            del self.list_services[(service_name, server_name)]
        except:
            pass

    def to_string(self, *p):
        """
        Format compatible for listing in ListBox
        """
        return "%s %s %s %s" % p
        
    def from_string(self, input):
        """
        Reverse format from ListBox
        """
        parts = input.split(' ')
        return parts


    def _filtered(self, service_name):
        filters=self.opts["service_filters"]
        if len(filters)==0:
            return True
        for filter in filters:
            #print "* trying filter: "+filter
            if service_name.startswith(filter.strip()):
                return True
        return False


        
        
