Cross-platform Multicast-DNS Service Browser
============================================

This application discovers the HTTP services announced on the local LAN segment 
using Multicast-DNS / Service-Discovery as per "draft-cheshire-dnsext-multicastdns-12.txt" & "draft-cheshire-dnsext-dns-sd-07.txt".

The application can be useful in a context such as discovery network equipment as per [LXI Standard](http://www.lxistandard.org/).

History
-------

0.1: initial release
0.2: added 'app_version' attribute to window title
0.4: made the 'config' parsing more lenient

Makefile
--------

" make wzip " : builds the Windows distribution zip file

" make install_linux [dir=INSTALL_DIR]" : install in ~/mdns_browser or INSTALL_DIR

Building the Windows distribution requires a full install of 'pygtk' version 2.x.
A zip file of the "mdns_browser-win32.zip" will be created in the current directory.

Usage Note
----------

On Linux, pygtk 2.x must be installed.

On Windows using from source: 
  cd src
  python mdns_browser.py
  

On Windows using zip distribution:
  unzip in any directory e.g. c:\Program Files\mdns_browser
  execute "mdns_browser.exe"


Configuration File
------------------

The configuration file "config" must be located in the same folder as the executable. The format is the following:

	# location of the help page
	[help]
  		url: http://some-website.com/
	# filter-out based on the following prefixes.
	# all entries matching the prefix will be filtered-out
	[service]
  		filters: prefix1, prefix2 ...`

Testing with Avahi
------------------

	avahi-publish -s testService _http._tcp 9000


Architecture
------------

Multi-threaded, agent based, message switch

*	Timer    : maintains the time-base
*	Querier  : performs periodic query
*	Listener : listens to incoming mDNS answers, issues "service" and "answer" messages
*	Comms    : performs In/Out socket communications
*	Cache    : maintains a cache of services
*	Ui       : presents the GUI


