import urllib2
import re
class Plugin( object ):
    def start( self ):
        raise NotImplementedError( "Should have implemented this" )
    def getName( self ):
        raise NotImplementedError( "Should have implemented this" )
        
    def getUrl( self, url ):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/13.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    
    def iMDBlink( self, url):
        match = re.search('tt[0-9]+',url)
        if match is None:
            return None
        return match.group(0)
