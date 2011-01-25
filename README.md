Cross-platform Multicast-DNS Service Browser

Tested on Windows XP and Linux Ubuntu.

Makefile
========

" make wzip " : builds the Windows distribution zip file

" make install_linux" : install in ~/mdns_browser


Architecture
============

Multi-threaded, agent based, message switch

*	Timer    : maintains the time-base
*	Querier  : performs periodic query
*	Listener : listens to incoming mDNS answers, issues "service" and "answer" messages
*	Comms    : performs In/Out socket communications
*	Cache    : maintains a cache of services
*	Ui       : presents the GUI


