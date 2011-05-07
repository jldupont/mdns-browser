"""
Created on 2011-01-12

@author: jldupont
"""
from Tkinter import *
import webbrowser

import mdns_browser.system.mswitch as mswitch
from mdns_browser.system.ui_base import UiAgentBase


class UiWindow(Frame): #@UndefinedVariable
    """
        Service Name ,  Server Name , Server Address , Server Port
    
    """
    def __init__(self):
        Frame.__init__(self, None)
        
        self.grid()
        self.lb=Listbox(self)
        self.lb.pack()
        
        self.bquit=Button(self, text="Quit", command=self.quit)
        
        self.lb.grid(row=0, column=0)
        self.bquit.grid(row=1, column=0)
        
        self.master.protocol("WM_DELETE_WINDOW", self.quit)
        
        self.list_services={}
        
    def quit(self):
        self.master.destroy()
        self.do_destroy()
        
    def do_destroy(self, *_):
        #print "ui.window: destroy"
        mswitch.publish(self, "__destroy__")
        mswitch.publish(self, "__quit__")
        
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


class UiAgent(UiAgentBase):
    def __init__(self, time_base, opts={}):
        UiAgentBase.__init__(self, time_base, ui_window_class=UiWindow, opts=opts)
        
        self.window = UiWindow()
        
    def do_updates(self):
        if self.window is not None:
            self.pub("services?")
        
    def h_service(self, service_name, server_name, server_port, addresses):
        
        ## Window might not be shown
        if self.window is None:
            return
        
        try:    
            self.window.add_service(service_name, server_name, server_port, addresses)
        except Exception,e:
            self.log("w", "Ui Window Error whilst adding a service (%s)" % e)
            
    def h_service_expired(self, service_name, server_name, server_port):
        """
        """
        ## Window might not be shown
        if self.window is None:
            return

        try:
            self.window.remove_service(service_name, server_name, server_port)
        except Exception,e:
            self.log("w", "Ui Window Error whilst removing a service (%s)" % e)
    
    
    def h___destroy__(self, *_):
        self.window=None
        
        
if __name__=="__main__":
    import sys
    ui=UiWindow()
    ui.mainloop()
    print "end!"
    mswitch.quit()
    sys.exit()
