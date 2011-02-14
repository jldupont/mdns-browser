"""
Created on 2011-01-12

@author: jldupont
"""
import gtk
import webbrowser

from   mdns_browser.system.base import mdispatch
import mdns_browser.system.mswitch as mswitch
from mdns_browser.system.ui_base import UiAgentBase


class UiWindow(object): #@UndefinedVariable
    """
        Service Name ,  Server Name , Server Address , Server Port
    
    """
    def __init__(self, opts):

        self.opts=opts
        
        self.window = gtk.Window()
        self.window.set_title("MDNS Browser - version %s" % opts["app_version"])

        self.list_services=gtk.ListStore(str, str, str, str)
        self.treeview = gtk.TreeView(self.list_services)
               
        #First column's cell
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Service Name")
        col.pack_start(cell, True)
        col.set_attributes(cell,text=0)
        self.treeview.append_column(col)

        snv=opts["server_name_column_visibility"]
        col = gtk.TreeViewColumn("Server Name")
        col.pack_start(cell, True)
        col.set_attributes(cell,text=1)
        col.set_visible(snv)
        self.treeview.append_column(col)

        sav=opts["server_address_column_visibility"]
        col = gtk.TreeViewColumn("Server Address")
        col.pack_start(cell, True)
        col.set_attributes(cell,text=2)
        col.set_visible(sav)
        self.treeview.append_column(col)

        spv=opts["server_port_column_visibility"]
        col = gtk.TreeViewColumn("Server Port")
        col.pack_start(cell, True)
        col.set_attributes(cell,text=3)
        col.set_visible(spv)
        self.treeview.append_column(col)

        self.treeview.connect("row-activated", self.row_activated)
        
        self.window.add(self.treeview)
               
        self.window.connect("destroy-event", self.do_destroy)
        self.window.connect("destroy",       self.do_destroy)
        self.window.present()
        self.window.show_all()
        
    def do_destroy(self, *_):
        #print "ui.window: destroy"
        mswitch.publish(self, "__destroy__")
        
    def add_service(self, service_name, server_name, server_port, addresses):
        for row in self.list_services:
            sn, sern, _a, _sp = row
            if service_name==sn and server_name==sern:
                return
        #print "!! Ui Window: adding service: %s" % service_name 
        if self._filtered(service_name):
            self.list_services.append([service_name, server_name, addresses["ipv4"], server_port])
        
    def remove_service(self, service_name, server_name, server_port):
        #print "!! Ui Window: removing: %s " % service_name
        for row in self.list_services:
            sn, sern, _a, _sp = row
            if service_name==sn and sern==server_name:
                self.list_services.remove(row.iter)    

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
            if service_name.startswith(filter):
                return True
        return False


class UiAgent(UiAgentBase):
    def __init__(self, time_base, opts={}):
        UiAgentBase.__init__(self, time_base, ui_window_class=UiWindow, opts=opts)
        
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
        