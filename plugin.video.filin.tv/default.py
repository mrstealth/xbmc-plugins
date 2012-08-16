#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import urllib
#import urllib2, sys, os, time
import urllib, re
import xbmcplugin,xbmcgui,xbmcaddon

import HTMLParser
h = HTMLParser.HTMLParser()

import CommonFunctions

common = CommonFunctions
common.plugin = "Youfreetv.net"
common.dbg = False # Default (True)
common.dbglevel = 3 # Default

pluginhandle = int(sys.argv[1])
__addon__    = xbmcaddon.Addon(id='plugin.video.filin.tv')

URL         = 'http://www.filin.tv'

def unescape(entity, encoding):
  if encoding == 'utf-8':
    return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
  elif encoding == 'cp1251':
    return HTMLParser.HTMLParser().unescape(entity).decode(encoding).encode('utf-8')

def get_url(string):
  return re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.xml', string)[0]

def recent(url):
    result = common.fetchPage({"link": url})

    print result["content"]
    print result["header"]

    if result["status"] == 200:
        content = common.parseDOM(result["content"], "div", attrs = { "id":"dle-content" })
        mainf = common.parseDOM(content, "div", attrs = { "class":"mainf" })

        if len(mainf):
            for i, div in enumerate(mainf):
                href = common.parseDOM(div, "a", ret="href")[0]
                # TODO: parse encoding from html meta tag
                title = unescape(common.parseDOM(div, "a")[0], 'cp1251')
                uri = sys.argv[0] + '?mode=SHOW&url=%s'%href

                item = xbmcgui.ListItem(title, iconImage="icon.png", thumbnailImage="icon.png")
                item.setInfo( type='video', infoLabels={'title': 'test', 'plot': 'Description'})
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)

    xbmcplugin.endOfDirectory(pluginhandle, True)

def show(url):
    result = common.fetchPage({"link": url})
    flashvars = common.parseDOM(result["content"], "embed", ret="flashvars")[0]
    url = get_url(flashvars)

    xml = common.fetchPage({"link": url})
    locations = common.parseDOM(xml["content"], "location")
    titles = common.parseDOM(xml["content"], "title")

    for i in range(0, len(locations)):
        uri = sys.argv[0] + '?mode=PLAY&url=%s'%locations[i]
        item = xbmcgui.ListItem(unescape(titles[i], 'utf-8'), iconImage="icon.png", thumbnailImage="icon.png")
        xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
        item.setProperty('IsPlayable', 'true')
    xbmcplugin.endOfDirectory(pluginhandle, True)

def play(url):
    item = xbmcgui.ListItem(path = url)
    xbmc.Player().play(url)

def get_params():
    param=[]
    paramstring=sys.argv[2]
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
channel=None

try:
    mode=params['mode'].upper()
except: pass

try:
    url=urllib.unquote_plus(params['url'])
except: pass

print "+++++++++++++++++ MODE ++++++++++++++++++++++"
print params

if mode == 'SHOW':
    show(url)
elif mode == 'PLAY':
    play(url)
elif mode == None:
    recent(URL)
