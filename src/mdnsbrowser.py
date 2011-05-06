"""
    MDNS Browser
    
    Created on 2011-01-13

    @author: jldupont
    
    History:
    0.1: initial release
    0.2: added version # to window title
    0.3: added (optional) config file
    
"""
APP_VERSION = "0.3"
APP_NAME="mdns_browser"
HELP_URL="https://github.com/jldupont/mdns-browser"
TIME_BASE=1000

import os
import sys

## Use sys.argv[0] because of py2exe  i.e. can't use __file__
cp=os.path.abspath(os.path.dirname(sys.argv[0])) 
sys.path.insert(0, cp)

## "config" file
from mdns_browser.system.config import Configuration
cfg = Configuration(os.path.join(cp, "config"))
                    
#import gobject  
#import gtk

gobject.threads_init()  #@UndefinedVariable

from mdns_browser.system import mswitch
from mdns_browser.agents import sup
from mdns_browser.agents import debug
from mdns_browser.agents import comms
from mdns_browser.agents import logger
from mdns_browser.agents import querier
from mdns_browser.agents import listener
from mdns_browser.agents import cache
from mdns_browser.agents.ui import UiAgent


def main():
    try:
        from mdns_browser.agents.tray import TrayAgent
        help_url=cfg.get("help", "url", HELP_URL)
        _ta=TrayAgent(APP_NAME, help_url)

        filters=cfg.get("service", "filters", "")
        try:     filterList=filters.split(",")
        except:  filterList=[]
            
        opts={
              "app_version": APP_VERSION
              ,"server_name_column_visibility":cfg.get("column", "server_name", "yes")=="yes"
              ,"server_port_column_visibility": cfg.get("column", "server_port", "yes")=="yes"
              ,"server_address_column_visibility":cfg.get("column", "server_port", "yes")=="yes"
              ,"service_filters": filterList
              }

        _ua=UiAgent(TIME_BASE, opts)
        gobject.timeout_add(TIME_BASE, _ua.tick)

        gtk.main()
        
    except Exception,e:
        print "** Exception: %s" % e
        mswitch.quit()
        sys.exit(1)

main()
