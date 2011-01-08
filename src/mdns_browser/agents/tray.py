"""
    Tray Icon Agent
        
    Created on 2010-08-16
    @author: jldupont
"""
__all__=["TrayAgent"]

import os
import gtk #@UnusedImport
import gtk.gdk
import webbrowser
import mdns_browser.system.mswitch as mswitch

class AppPopupMenu:
    def __init__(self, app):
        self.item_exit = gtk.MenuItem( "exit", True)
        self.item_show = gtk.MenuItem( "show", True)
        self.item_help = gtk.MenuItem( "help", True)

        self.item_show.connect( 'activate', app.show)
        self.item_help.connect( 'activate', app.help)
        self.item_exit.connect( 'activate', app.exit)
        
        self.menu = gtk.Menu()
        self.menu.append( self.item_show)
        self.menu.append( self.item_help)
        self.menu.append( self.item_exit)        
        self.menu.show_all()

    def show_menu(self, button, time):
        self.menu.popup( None, None, None, button, time)
        


class TrayAgent(object):
    def __init__(self, app_name, help_url):
        
        self.app_name=app_name
        self.help_url=help_url
        self.popup_menu=AppPopupMenu(self)
        
        self.tray=gtk.StatusIcon()
        self.tray.set_from_stock(gtk.STOCK_ABOUT)
        self.tray.set_visible(True)
        self.tray.set_tooltip(app_name)
        self.tray.connect('popup-menu', self.do_popup_menu)
        
    def do_popup_menu_activate(self, statusIcon):
        timestamp=gtk.get_current_event_time()
        self.popup_menu.show_menu(None, int(timestamp))
        
    def do_popup_menu(self, status, button, time):
        self.popup_menu.show_menu(button, time)

    def show(self, *_):
        mswitch.publish(self, "app_show")

    def exit(self, *p):
        mswitch.publish(self, "__quit__")
        gtk.main_quit()
        
    def help(self, *_):
        webbrowser.open(self.help_url)


