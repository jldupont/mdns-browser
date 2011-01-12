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
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.window = self.builder.get_object("ui_window")

        #self.bHelp=self.builder.get_object("bHelp")
        #self.bHelp.connect("clicked", self.on_help)
        
        self.window.connect("destroy-event", self.do_destroy)
        self.window.connect("destroy",       self.do_destroy)
        self.window.present()
        
    def do_destroy(self, *_):
        print "ui.window: destroy"
        mswitch.publish(self, "__destroy__")
        
        




class UiAgent(UiAgentBase):
    def __init__(self, time_base, glade_file_path):
        UiAgentBase.__init__(self, time_base, UiWindow, glade_file_path)
        
    def do_updates(self):
        pass
    
    
    def h___destroy__(self, *_):
        self.window=None
        