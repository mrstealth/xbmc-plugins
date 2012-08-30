#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.1
# -*- coding: utf-8 -*-

import urllib, re
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import HTMLParser
import CommonFunctions

common = CommonFunctions
common.plugin = "Filin.net"
common.dbg = False # Default (True)
common.dbglevel = 3 # Default

pluginhandle = int(sys.argv[1])
__addon__    = xbmcaddon.Addon(id='plugin.video.filin.tv')

URL         = 'http://www.filin.tv'

# TODO: find a better way of html decoding
#def format(text):
#    return re.sub(r'^(&.*;)$', '', text)

def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return entity.decode(encoding).encode('utf-8')

def get_url(string):
  return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.xml', string)[0]

#def menu():
#    name="[Categories]"
#    text = "[COLOR FF00FF00][&#1050;&#1072;&#1090;&#1077;&#1075;&#1086;&#1088;&#1080;&#1080;][/COLOR]"
#    name= unescape(text, "utf-8")
#    print name
#    item = xbmcgui.ListItem(name)
#    uri = sys.argv[0] + '?mode=CATEGORIES'
#    xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

#    getRecentItems(URL)
#    xbmcplugin.endOfDirectory(pluginhandle, True)

def getCategories(url):
    result = common.fetchPage({"link": url})

    if result["status"] == 200:
        content = common.parseDOM(result["content"], "div", attrs = { "class":"mcont" })
        categories = common.parseDOM(content, "option", ret="value")
        descriptions = common.parseDOM(content, "option")

        for i in range(0, len(categories)):
            uri = sys.argv[0] + '?mode=CATEGORIE&url=' + URL + '/x.php&categorie=' + categories[i]
            title = unescape(descriptions[i], 'cp1251')

            item = xbmcgui.ListItem(title)
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)

def getCategoryItems(url,categorie):
    url = url + "?onlyjanr=" + categorie
    response = common.fetchPage({"link": url})
    content = response['content']

    if response["status"] == 200:
        links = common.parseDOM(content, "a", ret="href")
        titles = common.parseDOM(content, "a")

        for i in range(0, len(links)):
          uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + "&thumbnail=#"

          if titles[i] == '':
            titles[i] = "[Empty]" #TODO: investigate title issue

          item = xbmcgui.ListItem(titles[i])
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)



# Get latest income from index page
def getRecentItems(url):
    text = "[COLOR FF00FF00][&#1050;&#1072;&#1090;&#1077;&#1075;&#1086;&#1088;&#1080;&#1080;][/COLOR]"
    if url==URL: xbmcItem('', unescape(text, "utf-8"), 'CATEGORIES')

    response = common.fetchPage({"link": url})

    if response["status"] == 200:
        content = common.parseDOM(response["content"], "div", attrs = { "id":"dle-content" })
        mainf = common.parseDOM(content, "div", attrs = { "class":"mainf" })
        block = common.parseDOM(content, "div", attrs = { "class":"block_text" })
        descs = common.parseDOM(content, "div", attrs = { "style":"display:inline;" })

        for i, div in enumerate(mainf):
            href = common.parseDOM(div, "a", ret="href")[0]
            thumbnail = common.parseDOM(block[i], "img", ret = "src")[0]
            if thumbnail[0] == '/': thumbnail = URL+thumbnail

            title = unescape(common.parseDOM(div, "a")[0], 'cp1251')
            uri = sys.argv[0] + '?mode=SHOW&url=' + href + '&thumbnail=' + thumbnail

            item = xbmcgui.ListItem(title)
            item.setProperty( "Fanart_Image", thumbnail )
            item.setInfo( type='Video', infoLabels={'title': title, 'plot': unescape(descs[i], 'cp1251')})
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)


    next = URL+'/page/2' if url[-1] == 'v' else URL+'/page/' + str(int(url[-1])+1)

    xbmcItem(next, ">>", 'NEXT')
    xbmc.executebuiltin('Container.SetViewMode(52)')
    xbmcplugin.endOfDirectory(pluginhandle, True)


def showItem(url, thumbnail, *description):
    result = common.fetchPage({"link": url})
    flashvars = common.parseDOM(result["content"], "embed", ret="flashvars")[0]
    url = get_url(flashvars)

    xml = common.fetchPage({"link": url})["content"]
    locations = common.parseDOM(xml, "location")
    titles = common.parseDOM(xml, "title")

#    t = common.parseDOM(xml, "title")
#    creators = common.parseDOM(xml, "creator")

    for i in range(0, len(locations)):
        uri = sys.argv[0] + '?mode=PLAY&url=%s'%locations[i]
        item = xbmcgui.ListItem(unescape(titles[i], 'utf-8'), thumbnailImage=thumbnail)
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
        item.setProperty('IsPlayable', 'true')

    xbmcplugin.endOfDirectory(pluginhandle, True)



def playItem(url):
    item = xbmcgui.ListItem(path = url)
    xbmc.Player().play(url)



def xbmcItem(url, title, mode):
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

params = get_params()

# TODO: code refactoring
url=None
mode=None
categorie=None
thumbnail=None

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

if mode == 'NEXT':
    getRecentItems(url)
elif mode == 'SHOW':
    showItem(url,thumbnail)
elif mode == 'PLAY':
    playItem(url)
elif mode == 'CATEGORIES':
    getCategories(URL)
elif mode == 'CATEGORIE':
    getCategoryItems(url, categorie)
elif mode == None:
    getRecentItems(URL)
