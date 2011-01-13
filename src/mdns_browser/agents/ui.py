"""
Created on 2011-01-12

@author: jldupont
"""
import os
import gtk
from Queue import Queue, Empty

from   mdns_browser.system.base import mdispatch
import mdns_browser.system.mswitch as mswitch
from mdns_browser.system.ui_base import UiAgentBase


class UiWindow(object): #@UndefinedVariable
    
    def __init__(self, glade_file):

        self.window = gtk.Window()
        self.window.set_title("MDNS Browser")

        self.list_services=gtk.ListStore(str)
        self.treeview = gtk.TreeView(self.list_services)
               
        #First column's cell
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Services")
        col.pack_start(cell, True)
        
        #the first column is always painted
        #cell.set_property('background-set' , True)
        #cell.set_property('foreground-set' , True)
        col.set_attributes(cell,text=0)
        
        self.treeview.append_column(col)
        self.window.add(self.treeview)
               
        self.window.connect("destroy-event", self.do_destroy)
        self.window.connect("destroy",       self.do_destroy)
        self.window.present()
        self.window.show_all()
        
    def do_destroy(self, *_):
        #print "ui.window: destroy"
        mswitch.publish(self, "__destroy__")
        
    def add_service(self, service_name, server_name, server_port, addresses):
        self.list_services.append([service_name])
        print "> added service: %s" % service_name



class UiAgent(UiAgentBase):
    def __init__(self, time_base, glade_file_path):
        UiAgentBase.__init__(self, time_base, UiWindow, glade_file_path)
        
    def do_updates(self):
        if self.window is not None:
            self.pub("services?")
        
    def h_service(self, service_name, server_name, server_port, addresses):
        
        ## Window might not be shown
        if self.window is None:
            return
        
        try:    
            self.window.add_service(service_name, server_name, server_port, addresses)
            ##print ">> service: %s" % service_name
        except Exception,e:
            self.log("w", "Ui Window Error whilst adding a service (%s)" % e)
            
    
    def h___destroy__(self, *_):
        self.window=None
        