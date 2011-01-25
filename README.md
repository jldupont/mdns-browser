Cross-platform Multicast-DNS Service Browser

Tested on Windows XP and Linux Ubuntu.

Makefile
========

" make wzip " : builds the Windows distribution zip file

" make install_linux [dir=INSTALL_DIR]" : install in ~/mdns_browser or INSTALL_DIR

Building the Windows distribution requires a full install of 'pygtk' version 2.x.
A zip file of the "mdns_browser-win32.zip" will be created in the current directory.

Usage Note
==========

On Linux, pygtk 2.x must be installed.

On Windows using from source: 
  cd src
  python mdns_browser.py
  

On Windows using zip distribution:
  unzip in any directory e.g. c:\Program Files\mdns_browser
  mdns_browser.exe


Architecture
============

Multi-threaded, agent based, message switch

*	Timer    : maintains the time-base
*	Querier  : performs periodic query
*	Listener : listens to incoming mDNS answers, issues "service" and "answer" messages
*	Comms    : performs In/Out socket communications
*	Cache    : maintains a cache of services
*	Ui       : presents the GUI


