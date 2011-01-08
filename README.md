Cross-platform Multicast-DNS Service Browser

*Project underway*

Architecture
============

Multi-threaded, agent based, message switch

*	Timer     : maintains the time-base
*	Querier   : performs periodic query
*	Listener  : listens to incoming mDNS answers
*	Comms     : performs In/Out socket communications
*	Cache     : maintains a cache of services
*	Presenter : presents the GUI


Jean-Lou Dupont
http://www.systemical.com/
