#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-

import urllib, re, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import HTMLParser
import CommonFunctions
import simplejson as json

from urllib2 import Request, urlopen, URLError, HTTPError
from flashplayer import * 

common = CommonFunctions
#common.plugin = "Filin.net"
#common.dbg = False # Default (True)
#common.dbglevel = 3 # Default

BASE_URL = 'http://www.filin.tv'
pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.filin.tv')
language      = Addon.getLocalizedString
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
addon_cache = xbmc.translatePath( Addon.getAddonInfo( "profile" ) )

# *** Python helpers ***
def remove_html_tags(data):     # Strip HTML tags
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def remove_extra_spaces(data):  # Remove more than one consecutive white space
    p = re.compile(r'\s+')
    return p.sub(' ', data)

def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return entity.decode(encoding).encode('utf-8')

def localize(string):
    return unescape(string, 'utf-8')
    
def colorize(string, color):
    text = "[COLOR " + color + "]" + string + "[/COLOR]"
    return text
    
def get_url(string):
  return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.xml', string)[0]
  
# TODO: find a better way of html decoding
#def format(text):
#    return re.sub(r'^(&.*;)$', '', text)

# *** XBMC helpers ***
def xbmcItem(url, title, mode, *args):
    item = xbmcgui.ListItem(title)
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)


def get_params():
    param=[]
    paramstring = sys.argv[2]

    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')

        if (params[len(params)-1]=='/'):
            params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')

        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param
    

# *** Addon helpers ***   
def getDescription(block):
    html = block[block.find('</h2>'):len(block)]
    return unescape(remove_extra_spaces(remove_html_tags(html)), 'cp1251')

def getThumbnail(block):
    thumbnail = common.parseDOM(block, "img", ret = "src")[0]
    if thumbnail[0] == '/': thumbnail = BASE_URL+thumbnail
    return thumbnail
    
def getTitle(block):
    title = common.parseDOM(block, "a")
    return unescape(title[len(title)-1], 'cp1251')

def getWatched():
    try:
        file_path = os.path.join( addon_cache , "watched.db" )
        with open(file_path) as infile:
            data = json.load(infile)
        return data
        
    except IOError, e:
        data = []
        return data
        

# *** UI functions ***    
def search():
    kbd = xbmc.Keyboard()
    kbd.setDefault('')
    kbd.setHeading(language(2002))
    kbd.doModal()
    keyword=''
    
    if kbd.isConfirmed():
        try:
            keyword = trans.detranslify(kbd.getText())
            keyword=keyword.encode("utf-8")
        except:
            keyword = kbd.getText()

    path = "/do=search"
    values = {'do' : 'search', 
              'subaction' : 'search',
              'story' : keyword, 
              'x' : '0',
              'y' : '0'}
              
    data = urllib.urlencode(values)        
    req = Request(BASE_URL+path, data)

    try:
        response = urlopen(req)
    except URLError, e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
    else:
        response = response.read()
        info = common.parseDOM(response, "div", attrs = { "id":"dle-info" })[0]
        content = common.parseDOM(response, "div", attrs = { "id":"dle-content" })
               
        if len(info) > 1:
            result = common.parseDOM(info, "div", attrs = { "class":"ssc2r" })[0]
            item = xbmcgui.ListItem(colorize('[' + unescape(result, 'cp1251') + ']', 'FFFF4000'))
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(pluginhandle, '', item, False)
        else:
            result = common.parseDOM(content, "span", attrs = { "class":"sresult" })[0]
            item = xbmcgui.ListItem(colorize('[' + unescape(result, 'cp1251') + ']', 'FF00FFF0'))
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(pluginhandle, '', item, False)
        
            mainf = common.parseDOM(content, "div", attrs = { "class":"mainf" })
            titles = common.parseDOM(mainf, "a")
            links = common.parseDOM(mainf, "a", ret = "href")
            
            for i in range(0, len(links)):    
                title = unescape(titles[i], 'cp1251')
                uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + "&thumbnail="
            
                item = xbmcgui.ListItem(title)
                
                # TODO: move to "addFavorite" function
                script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
                params = "add|%s"%links[i] + "|%s"%title
                runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
                item.addContextMenuItems([(localize(language(3001)), runner)])
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
     
    xbmcplugin.endOfDirectory(pluginhandle, True)
    

def getCategories(url):
    result = common.fetchPage({"link": url})

    if result["status"] == 200:
        content = common.parseDOM(result["content"], "div", attrs = { "class":"mcont" })
        categories = common.parseDOM(content, "option", ret="value")
        descriptions = common.parseDOM(content, "option")

        for i in range(0, len(categories)):
            uri = sys.argv[0] + '?mode=CATEGORIE&url=' + BASE_URL + '/x.php&categorie=' + categories[i]
            title = unescape(descriptions[i], 'cp1251')

            item = xbmcgui.ListItem(title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)


def getCategoryItems(url, categorie, page):  
    path = url + "?onlyjanr=" + categorie
    page = int(page)
        
    response = common.fetchPage({"link": path})
    content = response['content']

    if response["status"] == 200:
        links = common.parseDOM(content, "a", ret="href")
        titles = common.parseDOM(content, "a")
              
        if page == 1:
            min=0
            max = {True: page*20, False: len(links)}[len(links) > (page*20)]
        else:
            min=(page-1)*20
            max= {True: page*20, False: len(links)}[len(links) > (page*20)]
        
        for i in range(min, max):
          uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + "&thumbnail="
          
          if titles[i] == '': titles[i] = "[Unknown]" #TODO: investigate title issue
          item = xbmcgui.ListItem(titles[i])
          
          # TODO: move to "addFavorite" function
          script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
          params = "add|%s"%links[i] + "|%s"%titles[i]
          runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"


          item.addContextMenuItems([(localize(language(3001)), runner)])
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        if max >= 20 and max < len(links):
            uri = sys.argv[0] + '?mode=CNEXT&url=' + url + '&page=' + str(page+1) + '&categorie=' + categorie
            item = xbmcgui.ListItem(localize(language(3000)))
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  
     
        xbmcplugin.endOfDirectory(pluginhandle, True)


def listGenres():
    genres = [
                 'http://www.filin.tv/otechestvennue/',
                 'http://www.filin.tv/detectiv/',
                 'http://www.filin.tv/romance/',
                 'http://www.filin.tv/action/',
                 'http://www.filin.tv/fantastika/',
                 'http://www.filin.tv/kriminal/',
                 'http://www.filin.tv/comedi/',
                 'http://www.filin.tv/teleshou/',
                 'http://www.filin.tv/multfilms/',
                 'http://www.filin.tv/adventure/',
                 'http://www.filin.tv/fantasy/',
                 'http://www.filin.tv/horror/',
                 'http://www.filin.tv/drama/',
                 'http://www.filin.tv/history/',
                 'http://www.filin.tv/triller/',
                 'http://www.filin.tv/mystery/',
                 'http://www.filin.tv/sport/',
                 'http://www.filin.tv/musical/',
                 'http://www.filin.tv/dokumentalnii/',
                 'http://www.filin.tv/war/'
    ]
    
    
    for i in range(0, len(genres)):
        uri = sys.argv[0] + '?&url=' + genres[i] + '/'
        item = xbmcgui.ListItem(localize(language(1000+i)))
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    xbmcplugin.endOfDirectory(pluginhandle, True)
     
     
def listFavorites():
    string = Addon.getSetting('favorites')
    
    if len(string) == 0:
        item = xbmcgui.ListItem()
        item.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(pluginhandle, '', item, True)
    else:
        favorites = json.loads(string)
        for key in favorites:
    	   item = xbmcgui.ListItem(favorites[key])

    	   # TODO: show thumbnail (item = xbmcgui.ListItem(key, thumbnailImage=thumbnail))
    	   uri = sys.argv[0] + '?mode=SHOW&url=' + key + '&thumbnail='
    	   item.setInfo( type='Video', infoLabels={'title': favorites[key]})
    	   
    	   # TODO: move to "addFavorite" function 
    	   script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
    	   params = "remove|%s"%key + "|%s"%favorites[key]
    	   runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
    	   item.addContextMenuItems([(localize(language(3004)), runner)])
    	   xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)
       
    xbmcplugin.endOfDirectory(pluginhandle, True)


# Get latest income from index page
def getRecentItems(url):
    
    if url==BASE_URL: 
        xbmcItem('', colorize(localize('['+language(2002)+']'), "FF00FF00"), 'SEARCH')
        xbmcItem('', colorize(localize(language(2003)), "FF00FFF0"), 'FAVORITES')
        xbmcItem('', colorize(localize(language(2000)), "FF00FFF0"), 'CATEGORIES')
        xbmcItem('', colorize(localize(language(2001)), "FF00FFF0"), 'GENRES')
    
    response = common.fetchPage({"link": url})
    
    if response["status"] == 200:
        content = common.parseDOM(response["content"], "div", attrs = { "id":"dle-content" })
        mainf = common.parseDOM(content, "div", attrs = { "class":"mainf" })
        block = common.parseDOM(content, "div", attrs = { "class":"block_text" })
        descs = common.parseDOM(content, "div", attrs = { "style":"display:inline;" })

        for i, div in enumerate(mainf):
            href = common.parseDOM(div, "a", ret="href")[0]
            thumbnail = common.parseDOM(block[i], "img", ret = "src")[0]
            if thumbnail[0] == '/': thumbnail = BASE_URL+thumbnail
            
            title = unescape(common.parseDOM(div, "a")[0], 'cp1251')
            uri = sys.argv[0] + '?mode=SHOW&url=' + href + '&thumbnail=' + thumbnail

            item = xbmcgui.ListItem(title, thumbnailImage=thumbnail)
            item.setInfo( type='Video', infoLabels={'title': title, 'plot': unescape(descs[i], 'cp1251')})
            item.setProperty( "isFolder", 'True')

            # TODO: move to "addFavorite" function
            script = "special://home/addons/plugin.video.filin.tv/contextmenuactions.py"
            params = "add|%s"%href + "|%s"%title
            runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
                         
            item.addContextMenuItems([(localize(language(3001)), runner)])
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    next = url + '/page/2' if url.find("page") == -1 else url[:-1] + str(int(url[-1])+1)
 
    xbmcItem(next, localize(language(3000)), 'RNEXT')
    xbmc.executebuiltin('Container.SetViewMode(52)')
    xbmcplugin.endOfDirectory(pluginhandle, True)


def showItem(url, thumbnail):
    content = common.fetchPage({"link": url})["content"]
    block = common.parseDOM(content, "div", attrs = { "class":"ssc" })[0]
        
    if len(thumbnail) == 0: thumbnail = getThumbnail(block)
    title = getTitle(block)
    desc = getDescription(block)
          
    flashvars = common.parseDOM(content, "embed", ret="flashvars")[0]
    url = get_url(flashvars)

    xml = common.fetchPage({"link": url})["content"]
    locations = common.parseDOM(xml, "location")
    titles = common.parseDOM(xml, "title") 
    
    for i in range(0, len(locations)):
        uri = sys.argv[0] + '?mode=PLAY&url=%s'%locations[i]
        item = xbmcgui.ListItem(unescape(titles[i], 'utf-8'), thumbnailImage=thumbnail)
                         
        if locations[i] in getWatched():
            overlay = xbmcgui.ICON_OVERLAY_WATCHED
            info = {"Title": title, "Plot": desc, "overlay": overlay, "playCount": 1}
        else:
            info = {"Title": title, "Plot": desc}

        item.setInfo( type='Video', infoLabels=info)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
        
    xbmc.executebuiltin('Container.SetViewMode(52)')
    xbmcplugin.endOfDirectory(pluginhandle, True)


def playItem(url):
    item = xbmcgui.ListItem(path = url)
    player = FlashPlayer()
    player.play(url, item)
        
    while(1):
        xbmc.sleep(500)        


# MAIN()
params = get_params()

# TODO: code refactoring
url=None
mode=None
categorie=None
thumbnail=None
page=None

try:
    mode=params['mode'].upper()
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    categorie=params['categorie']
except: pass
try:
    thumbnail=urllib.unquote_plus(params['thumbnail'])
except: pass
try:
    page=params['page']
except: pass

if mode == 'RNEXT':
    getRecentItems(url)
elif mode == 'CATEGORIES':
    getCategories(BASE_URL)
elif mode == 'CATEGORIE':
    getCategoryItems(url, categorie, '1')
elif mode == 'CNEXT':
    getCategoryItems(url, categorie, page)
elif mode == 'SHOW':
    showItem(url,thumbnail)
elif mode == 'PLAY':
    playItem(url)
elif mode == 'GENRES':
    listGenres();
elif mode == 'SEARCH':
    search();
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None:
    url = BASE_URL if url == None else url
    getRecentItems(url)
