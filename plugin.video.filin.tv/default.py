# -*- coding: utf-8 -*-
#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0

import re
import urllib,urllib2,re,sys,os,time
import xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

common = CommonFunctions
common.plugin = "Youfreetv.net"
common.dbg = False # Default (True)
common.dbglevel = 3 # Default

pluginhandle = int(sys.argv[1])
__addon__    = xbmcaddon.Addon(id='plugin.video.filin.tv') 

URL         = 'http://www.filin.tv'
    
def recent(url):
    result = common.fetchPage({"link": url})

    if result["status"] == 200:
        content = common.parseDOM(result["content"], "div", attrs = { "id":"dle-content" })  
        mainf = common.parseDOM(content, "div", attrs = { "class":"mainf" })

        if len(mainf):
            for i, div in enumerate(mainf):
                href = common.parseDOM(div, "a", ret="href")[0]
                title = common.parseDOM(div, "a")[0]
                uri = sys.argv[0] + '?mode=SHOW&url=%s'%href
                 
                item = xbmcgui.ListItem(title, iconImage="icon.png", thumbnailImage="icon.png")
                item.setInfo( type='video', infoLabels={'title': 'test', 'plot': 'Description'})
                item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(pluginhandle, uri, item)

    xbmcplugin.endOfDirectory(pluginhandle, True, True, False)     
     
     
def show(url):
    print "*** SHOW " + url
    result = common.fetchPage({"link": url})
    
    print result
    uri = sys.argv[0] + '?mode=PLAY&url=%s'%href
    item = xbmcgui.ListItem("test", iconImage="icon.png", thumbnailImage="icon.png")
    item.setInfo( type='video', infoLabels={'title': 'test', 'plot': 'Description'})
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(pluginhandle, uri, item)    
    
    xbmcplugin.endOfDirectory(pluginhandle, True)  
    

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
    mode=params['mode']
except: pass

try:
    url=urllib.unquote_plus(params['url'])
except: pass

if mode == None:
    print "**** DEFAULT MODE"
    recent(URL)
elif mode == 'SHOW': 
    print "**** MODE " + mode
    show(url)
