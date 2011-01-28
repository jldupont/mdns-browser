"""
    MDNS Browser
    
    Created on 2011-01-13

    @author: jldupont
    
    History:
    0.1: initial release
    0.2: added version # to window title
    
"""
APP_VERSION = "0.2"
APP_NAME="mdns_browser"
HELP_URL="https://github.com/jldupont/mdns-browser"
TIME_BASE=1000

import os
import sys

## Use sys.argv[0] because of py2exe
cp=os.path.abspath(os.path.dirname(sys.argv[0])) 
sys.path.insert(0, cp)

import gobject  
import gtk

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
        _ta=TrayAgent(APP_NAME, HELP_URL)

        _ua=UiAgent(TIME_BASE, app_version=APP_VERSION)
        gobject.timeout_add(TIME_BASE, _ua.tick)

        gtk.main()
        
    except Exception,e:
        print "** Exception: %s" % e
        mswitch.quit()
        sys.exit(1)

main()
