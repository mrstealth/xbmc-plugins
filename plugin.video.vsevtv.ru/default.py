# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.1

import xbmcplugin,xbmcgui,xbmcaddon
import urllib, CommonFunctions
import simplejson as json

common = CommonFunctions

pluginhandle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.vsevtv.ru')
language      = Addon.getLocalizedString
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')

BASE_URL   = 'http://tv.vsevtv.ru/tv.html'
    
def get_groups(url):
    page = common.fetchPage({"link": url})

    if page["status"] == 200:       
        select = common.parseDOM(page["content"], "SELECT", attrs = { "id":"ch" }) 
        optgroups = common.parseDOM(select, "optgroup", ret="label")
        options = common.parseDOM(select, "optgroup")

        for i in range(len(optgroups)):
            uri = sys.argv[0] + '?mode=SHOW'
            uri += '&url=' + urllib.quote_plus(BASE_URL)
            uri += '&title=' + optgroups[i]
            
            item = xbmcgui.ListItem(optgroups[i], iconImage=addon_icon, thumbnailImage=addon_icon)
            item.setInfo( type='video', infoLabels={'title': optgroups[i]})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item, True)             
       
    xbmcplugin.endOfDirectory(pluginhandle, True, True, True) 
        
def get_channels(url, title):
    page = common.fetchPage({"link": url})

    if page["status"] == 200:       
        select = common.parseDOM(page["content"], "SELECT", attrs = { "id":"ch" }) 
        optgroups = common.parseDOM(select, "optgroup", ret="label")
        options = common.parseDOM(select, "optgroup")
            
        channels = options[optgroups.index(title)]
        titles = common.parseDOM(channels, "option")
        links = common.parseDOM(channels, "option", ret="value")

        for i,href in enumerate(links):
            uri = sys.argv[0] + '?mode=PLAY'
            uri += '&url=' + urllib.quote_plus(links[i])
            uri += '&title=' + titles[i]
            
            item = xbmcgui.ListItem(titles[i], iconImage=addon_icon, thumbnailImage=addon_icon)
            item.setInfo( type='video', infoLabels={'title': titles[i]})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(pluginhandle, uri, item)
       
    xbmcplugin.endOfDirectory(pluginhandle, True, True, True)
    
       
def play_url(url, title):
    item = xbmcgui.ListItem(path = url) 
    xbmcplugin.setResolvedUrl(pluginhandle, True, item)

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

url=None
mode=None
title=None

try:
    mode=params['mode']
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    title=params['title']
except: pass

if mode == 'PLAY':
    play_url(url, title)
elif mode == 'SHOW': 
    get_channels(BASE_URL, title)
elif mode == None: 
    get_groups(BASE_URL)
