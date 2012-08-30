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


#Strip HTML tags
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)


#Remove more than one consecutive white spaces:

def remove_extra_spaces(data):
    p = re.compile(r'\s+')
    return p.sub(' ', data)


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


def getDescription(block):
    html = block[block.find('</h2>'):len(block)]
    return unescape(remove_extra_spaces(remove_html_tags(html)), 'cp1251')

def getThumbnail(block):
    thumbnail = common.parseDOM(block, "img", ret = "src")[0]
    if thumbnail[0] == '/': thumbnail = URL+thumbnail
    return thumbnail
    
def getTitle(block):
    title = common.parseDOM(block, "a")
    return unescape(title[len(title)-1], 'cp1251')
    
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
            max = {True: page*10, False: len(links)}[len(links) > (page*10)]
        else:
            min=(page-1)*10
            max= {True: page*10, False: len(links)}[len(links) > (page*10)]
        
        for i in range(min, max):
          # html parsing is to slow, find a better way for getting posters
          #content = common.fetchPage({"link": links[i]})["content"]
          #ssc = common.parseDOM(content, "div", attrs = { "class":"ssc" })
          #thumbnail = common.parseDOM(ssc, "img", ret = "src")[0]
          #if thumbnail[0] == '/': thumbnail = URL+thumbnail                   
          #uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + "&thumbnail=" + thumbnail
          
          uri = sys.argv[0] + '?mode=SHOW&url=' + links[i] + "&thumbnail="
          
          if titles[i] == '': titles[i] = "[Empty]" #TODO: investigate title issue

          item = xbmcgui.ListItem(titles[i])
          xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

        if max >= 10 and max < len(links):
            uri = sys.argv[0] + '?mode=CNEXT&url=' + url + '&page=' + str(page+1) + '&categorie=' + categorie
            item = xbmcgui.ListItem('>>')
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
                 'http://www.filin.tv/dokumentalnii/'
    ]
    
    
    for i in range(0, len(genres)):
        uri = sys.argv[0] + '?&url=' + genres[i]
        item = xbmcgui.ListItem(genres[i])
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)  

    
    xbmcplugin.endOfDirectory(pluginhandle, True)
     
    

# Get latest income from index page
def getRecentItems(url):
    categories = "[COLOR FF00FF00][&#1050;&#1072;&#1090;&#1077;&#1075;&#1086;&#1088;&#1080;&#1080;][/COLOR]"
    genres = "[COLOR FF00FF00]&#1046;&#1072;&#1085;&#1088;&#1099; (&#1085;&#1086;&#1074;&#1099;&#1077; &#1087;&#1086;&#1089;&#1090;&#1091;&#1087;&#1083;&#1077;&#1085;&#1080;&#1103;)[/COLOR]"
    
    if url==URL: 
        xbmcItem('', unescape(categories, "utf-8"), 'CATEGORIES')
        xbmcItem('', unescape(genres, "utf-8"), 'GENRES')
    

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
            item.setInfo( type='Video', infoLabels={'title': title, 'plot': unescape(descs[i], 'cp1251')})
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)


    next = URL+'/page/2' if url[-1] == 'v' else URL+'/page/' + str(int(url[-1])+1)

    xbmcItem(next, ">>", 'RNEXT')
    xbmc.executebuiltin('Container.SetViewMode(52)')
    xbmcplugin.endOfDirectory(pluginhandle, True)

#import string 

def showItem(url, thumbnail):
    content = common.fetchPage({"link": url})["content"]
    block = common.parseDOM(content, "div", attrs = { "class":"ssc" })[0]
        
    if len(thumbnail) == 0: thumbnail = getThumbnail(block)
    desc = getDescription(block) 
          
    flashvars = common.parseDOM(content, "embed", ret="flashvars")[0]
    url = get_url(flashvars)

    xml = common.fetchPage({"link": url})["content"]
    locations = common.parseDOM(xml, "location")
    titles = common.parseDOM(xml, "title")
    
    print url

#    t = common.parseDOM(xml, "title")
#    creators = common.parseDOM(xml, "creator")

    title = getTitle(block)

    for i in range(0, len(locations)):
        uri = sys.argv[0] + '?mode=PLAY&url=%s'%locations[i]
        item = xbmcgui.ListItem(unescape(titles[i], 'utf-8'), thumbnailImage=thumbnail)
        item.setInfo( type='Video', infoLabels={'title': title, 'plot': desc})
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
        
    xbmc.executebuiltin('Container.SetViewMode(52)')
    xbmcplugin.endOfDirectory(pluginhandle, True)



def playItem(url):
    item = xbmcgui.ListItem(path = url)
    xbmc.Player().play(url)



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
elif mode == 'CNEXT':
    getCategoryItems(url, categorie, page)
elif mode == 'SHOW':
    showItem(url,thumbnail)
elif mode == 'PLAY':
    playItem(url)

elif mode == 'GENRES':
    listGenres();
elif mode == 'CATEGORIES':
    getCategories(URL)
elif mode == 'CATEGORIE':
    getCategoryItems(url, categorie, '1')
elif mode == None:
    url = {True: url, False: URL}[url == None]
    
    getRecentItems(url)
    
# Add alternative view mode for genres 
# example pagination: http://www.filin.tv/dokumentalnii/page/2/
# http://www.filin.tv/otechestvennue/
# http://www.filin.tv/detectiv/
# http://www.filin.tv/romance/
# http://www.filin.tv/action/
# http://www.filin.tv/fantastika/
# http://www.filin.tv/kriminal/
# http://www.filin.tv/comedi/
# http://www.filin.tv/teleshou/
# http://www.filin.tv/multfilms/
# http://www.filin.tv/adventure/
# http://www.filin.tv/fantasy/
# http://www.filin.tv/horror/
# http://www.filin.tv/drama/
# http://www.filin.tv/history/
# http://www.filin.tv/triller/
# http://www.filin.tv/mystery/
# http://www.filin.tv/sport/
# http://www.filin.tv/musical/
# http://www.filin.tv/dokumentalnii/


# EXAMPLES
# >>> foo = [
# ...            'some string',
# ...         'another string',
# ...           'short string'
# ... ]
# >>> print foo
# ['some string', 'another string', 'short string']
# 
# >>> bar = 'this is ' \
# ...       'one long string ' \
# ...           'that is split ' \
# ...     'across multiple lines'
# >>> print bar
# this is one long string that is split across multiple lines
