"""
    Config Parser helper
    
    NOTE: not useful as Config.read()
        doesn't generate an exception if the path is invalid
    
    @author: Jean-Lou Dupont
"""
import ConfigParser

class Configuration(object):
    
    def __init__(self, path, debug=False):
        self.Config=ConfigParser.ConfigParser()
        self.Config.read(path)
    
    def get(self, section, entry, default=""):
        try:
            value=self.Config.get(section, entry)
            return value
        except:
            return default
    
    def sections(self):
        return self.Config.sections()
    
if __name__=="__main__":
    import os
    path=os.path.dirname(__file__)+"/testConfig"
    
    c=Configuration(path)
    print c.sections()
    
    c2=Configuration("", debug=True)
    print c2.sections()
