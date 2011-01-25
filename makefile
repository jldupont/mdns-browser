# @author: Jean-Lou Dupont
#
# @version: 1
#

PRJ=mdns_browser

DEFAULT_DIR=~/${PRJ}
INSTALL_DIR=$(dir)

ifeq ($(dir),)
	INSTALL_DIR=${DEFAULT_DIR}
endif

all:
	@echo "Options:"
	@echo "  wzip: build windows distribution"
	@echo "  install_linux (dir=): install locally"

wzip:
	@echo "Building Windows distribution zip file"
	@echo "** The utility '7-zip' is required"
	cd src && python setup_exe.py py2exe
	7z a -tzip mdns_browser-win32 ./src/dist/*.*
	
install_linux:
	@echo "Installing in ${INSTALL_DIR}"
	@install -d ${INSTALL_DIR}
	@install -d ${INSTALL_DIR}/src
	@install -d ${INSTALL_DIR}/src/mdns_browser
	@install -d ${INSTALL_DIR}/src/mdns_browser/agents
	@install -d ${INSTALL_DIR}/src/mdns_browser/mdns
	@install -d ${INSTALL_DIR}/src/mdns_browser/system
	
	
	@cp $(CURDIR)/mdns_browser         ${INSTALL_DIR}/mdns_browser
	@cp $(CURDIR)/src/mdns_browser.py  ${INSTALL_DIR}/src/mdns_browser.py
	
	@cp -R $(CURDIR)/src/mdns_browser   ${INSTALL_DIR}/src
	
.PHONY: wzip install_linux