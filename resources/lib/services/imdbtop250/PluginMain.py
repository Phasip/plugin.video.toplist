from plugin import Plugin
from BeautifulSoup import BeautifulSoup
import HTMLParser

class PluginMain( Plugin ):
    def getName( self ):
        return 'iMDB top 250';
	
    def loadList( self ):
        #Return a list [imdbid, texname]
        data = Plugin.getUrl(self,'http://akas.imdb.com/chart/top')
        #print("Data: " + data)
        bs = BeautifulSoup(data,convertEntities=BeautifulSoup.HTML_ENTITIES)
        if bs is None:
            print("Fail to read imdb toplist")
            return None
            
        tables = bs.findAll('table')
        for table in tables:
            rows = table.findAll('tr')
            if len(rows) < 251:
                continue
            ret = []
            i = iter(rows);
            next(i) #Ignore first row with the names.
            h = HTMLParser.HTMLParser()
            for row in i:
                link = row.find('a',href=True)
                #TODO: I am probably doing something wrong with beautifulsoup
                name = h.unescape(link.getText())
                imdb_id = Plugin.iMDBlink(self, link['href'])
                ret.append([name,imdb_id])
            return ret
        return None
	
