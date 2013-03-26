# -*- coding: utf-8 -*- 

import os,imp,sys
import xbmc,xbmcaddon,xbmcgui,xbmcplugin
import urllib,urllib2
import json

__addon__      = xbmcaddon.Addon()
__author__     = __addon__.getAddonInfo('author')
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode("utf-8")
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) ).decode("utf-8")

sys.path.append (__resource__)
SERVICE_DIR    = os.path.join(__cwd__, "resources", "lib", "services")


def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = urllib.unquote_plus(paramSplits[1])
    return paramDict
        
def load_from_file(filepath):
    class_inst = None
    expected_class = 'PluginMain'

    mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

    if file_ext.lower() == '.py':
        py_mod = imp.load_source(mod_name, filepath)

    elif file_ext.lower() == '.pyc':
        py_mod = imp.load_compiled(mod_name, filepath)

    if hasattr(py_mod, expected_class):
        class_inst = py_mod.PluginMain() 

    return class_inst
    
def listServices():
    service_list = []
    for name in os.listdir(SERVICE_DIR):
        p = os.path.join(SERVICE_DIR,name);
        scriptfile = os.path.join(p,"PluginMain.py");
        if os.path.isdir(p) and os.path.isfile(scriptfile):# and __addon__.getSetting( name ) == "true":
            c = load_from_file(scriptfile);
            service_list.append([c,scriptfile])
    return service_list

def addLink(name,url,mode,iconimage,desc,length=""):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc, "Duration": length } )
    liz.setProperty('IsPlayable', 'true')
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
    return ok

def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
    
def addMovie(name, info):
    if info is None:
        u=sys.argv[0]+"?url="+urllib.quote_plus("")+"&mode="+urllib.quote_plus(pluginName)
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage="")
        liz.setInfo( type="Disabled", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        return
        
    print("Info: " + str(info))
    u=info['file']
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=info['thumbnail'])
    if 'runtime' in info:
        info['duration'] = info['runtime']/60
    liz.setInfo( type="Video", infoLabels=info )
    #x = { "Title": "name", "Plot": "desc", "Duration": "120" }
    #liz.setInfo( type="Video", infoLabels=x )
    #print(x)
    #print(info)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    return ok
    
def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input
        
settings = xbmcaddon.Addon(id='plugin.video.toplist')
pluginhandle = int(sys.argv[1])
params = parameters_string_to_dict(sys.argv[2])
pluginName = params.get('mode');
if (pluginName is None) or (pluginName == ""):
    for [plugin, pluginname] in listServices():
        addDir(plugin.getName(),"",pluginname,"")
    xbmcplugin.endOfDirectory(pluginhandle);
    sys.exit();


plugin = load_from_file(pluginName);

movielistCommand='{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies","params" : { "properties" : ["title", "genre", "year", "rating", "director", "trailer", "tagline", "plot", "plotoutline", "originaltitle", "lastplayed", "playcount", "writer", "studio", "mpaa", "cast", "country", "imdbnumber", "runtime", "set", "showlink", "streamdetails", "top250", "votes", "fanart", "thumbnail", "file", "sorttitle", "resume", "setid", "dateadded", "tag", "art"], "sort": { "order":"ascending"} }, "id": 1}';
result = xbmc.executeJSONRPC( movielistCommand )
json = json.loads(result)
movieList = convert(json['result']['movies'])

idmap = {}
for movie in movieList:
	#print("Movie: " + movie['title'])
	idmap[movie['imdbnumber']] = movie
	
#name,imdbid
toplist = plugin.loadList();
i = 0
for [name,imdb] in toplist:
    i += 1
    t = "%02d" % (i,)
    if imdb in idmap:
        allinfo = idmap[imdb]
        addMovie(t + "  -  " + name,allinfo)
    else:
        addMovie(t + "  -  " + name,None)
		
xbmcplugin.endOfDirectory(pluginhandle);
