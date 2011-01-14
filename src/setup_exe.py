'''
    For packaging in .exe for Windows
    
    Created on 2011-01-13

    @author: jldupont
'''
from distutils.core import setup
import py2exe

setup(
    name = 'mdns_browser',

    windows = [
                      {
                          'script': 'mdns_browser.py',
                      }
                  ],
    options = {
                  'py2exe': {
                      'packages':'encodings',
                      'includes': 'cairo, pango, pangocairo, atk, gobject, glib, gio',
                  }
              },
)