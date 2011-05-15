'''
Created on 2011-05-05

@author: jldupont
'''

__author__  ="Jean-Lou Dupont"
__version__ ="0.4.1"

from distutils.core import setup
from setuptools import find_packages

setup(name=         'mdnsbrowser',
      version=      __version__,
      description=  'Multicast DNS service browser',
      author=       __author__,
      author_email= 'jl@jldupont.com',
      url=          'http://www.systemical.com/doc/opensource',
      package_dir=  {'': "src",},
      packages=     find_packages("src"),
      scripts=      ['src/mdnsbrowser', 'src/mdnsbrowser.py',
                     ],
      package_data = {
                      '':[ "*.gif", "*.png", "*.jpg" ],
                      },
      include_package_data=True,                      
      zip_safe=False
      )
