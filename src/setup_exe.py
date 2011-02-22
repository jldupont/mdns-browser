'''
    For packaging in .exe for Windows
    
    Created on 2011-01-13

    @author: jldupont
'''
__version__="0.4"
from distutils.core import setup
import py2exe

setup(
    name = 'mdns_browser',
    version=      __version__,
    windows = [
                {
                 'script': 'mdns_browser.py',
                }
            ]
    ,data_files=['config', ]
    #,include_package_data=True
    #,package_data = { '':[ "config", ], }    
    ,options = {
                  'py2exe': {
                      'packages':'encodings'
                      ,'includes': 'cairo, pango, pangocairo, atk, gobject, glib, gio'
                      #,"bundle_files": 1
                  }
              },
)